
import json
import logging
import re
import time
from pathlib import Path
from urllib.parse import quote

import requests
from requests.exceptions import RequestException


# ==================================================
# 1. PATHS AND LOGGING
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
LOG_DIR = BASE_DIR / "logs"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_DIR / "app.log",
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"

HEADERS = {
    "User-Agent": (
        "CompanyResearchProject/1.0 "
        "(educational data collection)"
    )
}


# ==================================================
# 2. AUTOMATIC COMPANY DISCOVERY SETTINGS
# No manually written company-name list is needed.
# ==================================================

DISCOVERY_QUERIES = [
    "company",
    "corporation",
    "multinational corporation",
    "technology company",
    "manufacturing company",
    "pharmaceutical company",
    "automotive company",
    "retail company",
    "financial services company",
    "telecommunications company",
]

MAX_DISCOVERED_PAGES = 100
SEARCH_RESULTS_PER_PAGE = 50
MAX_SEARCH_PAGES_PER_QUERY = 2


# ==================================================
# 3. CREATE SAFE JSON FILE NAMES
# ==================================================

def make_filename(company_name):
    filename = re.sub(
        r"[^a-z0-9]+",
        "_",
        company_name.lower(),
    ).strip("_")

    return filename + ".json"


# ==================================================
# 4. AUTOMATICALLY DISCOVER WIKIPEDIA PAGES
# ==================================================

def discover_company_names():
    """Discover company-related Wikipedia page titles."""
    discovered = {}

    logger.info("Starting automatic Wikipedia discovery.")

    for query in DISCOVERY_QUERIES:
        offset = 0

        for page_number in range(MAX_SEARCH_PAGES_PER_QUERY):
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srnamespace": 0,
                "srlimit": SEARCH_RESULTS_PER_PAGE,
                "sroffset": offset,
            }

            response = None

            try:
                response = requests.get(
                    WIKIPEDIA_API,
                    params=params,
                    headers=HEADERS,
                    timeout=30,
                )
                response.raise_for_status()

                result = response.json()
                search_results = result.get(
                    "query", {}
                ).get("search", [])

                if not search_results:
                    break

                for item in search_results:
                    title = item.get("title", "").strip()

                    if title:
                        discovered[title.casefold()] = title

                logger.info(
                    "Search '%s': received %d results.",
                    query,
                    len(search_results),
                )

                continuation = result.get("continue", {})
                next_offset = continuation.get("sroffset")

                if next_offset is None:
                    break

                offset = next_offset

                time.sleep(1)

            except requests.exceptions.HTTPError as error:
                status_code = (
                    error.response.status_code
                    if error.response is not None
                    else None
                )

                logger.error(
                    "HTTP error during discovery for '%s': %s",
                    query,
                    status_code,
                )
                break

            except requests.exceptions.Timeout:
                logger.warning(
                    "Discovery timed out for query: %s",
                    query,
                )
                break

            except RequestException:
                logger.exception(
                    "Network error during discovery: %s",
                    query,
                )
                break

            except (ValueError, KeyError, TypeError):
                logger.exception(
                    "Invalid discovery response for: %s",
                    query,
                )
                break

            except Exception:
                logger.exception(
                    "Unexpected discovery error for: %s",
                    query,
                )
                break

            finally:
                if response is not None:
                    response.close()

    company_names = list(discovered.values())
    company_names = company_names[:MAX_DISCOVERED_PAGES]

    logger.info(
        "Discovery completed. Unique candidate pages: %d",
        len(company_names),
    )

    return company_names


# ==================================================
# 5. COLLECT COMPANY PAGE DATA WITH ERROR HANDLING
# ==================================================

def collect_company_data(company_name):
    logger.info("Starting collection: %s", company_name)

    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": 1,
        "redirects": 1,
        "titles": company_name,
    }

    max_attempts = 4

    for attempt in range(1, max_attempts + 1):
        response = None

        try:
            response = requests.get(
                WIKIPEDIA_API,
                params=params,
                headers=HEADERS,
                timeout=30,
            )

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")

                try:
                    wait_seconds = (
                        int(retry_after)
                        if retry_after
                        else min(10 * attempt, 60)
                    )
                except (ValueError, TypeError):
                    wait_seconds = min(10 * attempt, 60)

                logger.warning(
                    "Rate limited for %s. Waiting %d seconds.",
                    company_name,
                    wait_seconds,
                )

                if attempt == max_attempts:
                    logger.error(
                        "Rate limit persisted for %s",
                        company_name,
                    )
                    return None

                response.close()
                response = None
                time.sleep(wait_seconds)
                continue

            response.raise_for_status()
            result = response.json()

            pages = result.get(
                "query", {}
            ).get("pages", {})

            if not pages:
                logger.warning(
                    "No Wikipedia page found for %s",
                    company_name,
                )
                return None

            page = next(iter(pages.values()))

            if "missing" in page:
                logger.warning(
                    "Wikipedia page missing: %s",
                    company_name,
                )
                return None

            title = page.get("title", company_name)
            description = page.get("extract", "").strip()

            if not description:
                logger.warning(
                    "Empty description for %s",
                    company_name,
                )
                return None

            # Basic relevance check.
            # This reduces unrelated pages but cannot guarantee
            # that every returned page is a company.
            company_terms = (
                "company",
                "corporation",
                "conglomerate",
                "enterprise",
                "manufacturer",
                "business",
                "subsidiary",
                "firm",
            )

            text_to_check = (
                title + " " + description[:3000]
            ).casefold()

            if not any(
                term in text_to_check
                for term in company_terms
            ):
                logger.info(
                    "Skipping likely unrelated page: %s",
                    title,
                )
                return None

            company_data = {
                "company_name": title,
                "wikipedia_title": title,
                "source": (
                    "https://en.wikipedia.org/wiki/"
                    + quote(title.replace(" ", "_"), safe="()")
                ),
                "description": description,
            }

            logger.info(
                "Successfully collected: %s",
                title,
            )

            return company_data

        except requests.exceptions.HTTPError as error:
            status_code = (
                error.response.status_code
                if error.response is not None
                else None
            )

            if (
                status_code is not None
                and 400 <= status_code < 500
                and status_code != 429
            ):
                logger.error(
                    "Non-retryable HTTP error for %s: %s",
                    company_name,
                    status_code,
                )
                return None

            logger.warning(
                "HTTP error for %s on attempt %d/%d",
                company_name,
                attempt,
                max_attempts,
            )

        except requests.exceptions.Timeout:
            logger.warning(
                "Timeout for %s on attempt %d/%d",
                company_name,
                attempt,
                max_attempts,
            )

        except RequestException:
            logger.exception(
                "Network error for %s",
                company_name,
            )

        except (ValueError, KeyError, TypeError):
            logger.exception(
                "Invalid response data for %s",
                company_name,
            )
            return None

        except Exception:
            logger.exception(
                "Unexpected error for %s",
                company_name,
            )
            return None

        finally:
            if response is not None:
                response.close()

        if attempt < max_attempts:
            wait_seconds = 5 * attempt

            logger.info(
                "Retrying %s after %d seconds",
                company_name,
                wait_seconds,
            )

            time.sleep(wait_seconds)

    logger.error(
        "Collection failed after %d attempts: %s",
        max_attempts,
        company_name,
    )

    return None


# ==================================================
# 6. SAVE JSON WITHOUT OVERWRITING EXISTING FILES
# ==================================================

def save_company_data(company_name, company_data):
    file_path = RAW_DATA_DIR / make_filename(company_name)

    try:
        if file_path.exists():
            logger.info(
                "Existing file preserved: %s",
                file_path.name,
            )
            return False

        with file_path.open(
            "x",
            encoding="utf-8",
        ) as file:
            json.dump(
                company_data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        logger.info("Saved file: %s", file_path.name)
        return True

    except FileExistsError:
        logger.info(
            "Existing file preserved: %s",
            file_path.name,
        )
        return False

    except (OSError, TypeError, ValueError):
        logger.exception(
            "Could not save data for %s",
            company_name,
        )
        return False


# ==================================================
# 7. PROCESS DISCOVERED PAGES AUTOMATICALLY
# ==================================================

def main():
    logger.info("Automatic company collection started.")

    company_names = discover_company_names()

    if not company_names:
        logger.error(
            "No pages discovered. Collection stopped."
        )
        return

    successful = 0
    failed = 0
    skipped = 0

    logger.info(
        "Processing %d discovered candidate pages.",
        len(company_names),
    )

    for company_name in company_names:
        file_path = RAW_DATA_DIR / make_filename(company_name)

        if file_path.exists():
            logger.info(
                "Skipping existing file: %s",
                file_path.name,
            )
            skipped += 1
            continue

        company_data = collect_company_data(company_name)

        if company_data is None:
            failed += 1
            continue

        if save_company_data(company_name, company_data):
            successful += 1
        else:
            failed += 1

        # Pause between collection requests.
        time.sleep(2)

    logger.info(
        "Collection finished | Discovered: %d | "
        "Saved: %d | Failed: %d | Skipped: %d",
        len(company_names),
        successful,
        failed,
        skipped,
    )


# ==================================================
# 8. START THE PROGRAM
# ==================================================

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        logger.warning("Collection interrupted by user.")

    except Exception:
        logger.exception(
            "Unexpected error in main process."
        )
