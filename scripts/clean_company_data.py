
import json
import logging
import re
from pathlib import Path

# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(parents=True, exist_ok=True)

# Save cleaning activity in a log file
logging.basicConfig(
    filename=LOG_DIR / "clean_company_data.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


def clean_text(text):
    """Clean Wikipedia formatting and common text problems."""
    if not isinstance(text, str):
        return text

    # Fix common encoding problems
    replacements = {
        "â‚¹": "₹",
        "â€™": "'",
        "â€œ": '"',
        "â€": '"',
        "â€“": "-",
        "â€”": "-",
        "\u00a0": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove Wikipedia section headings and everything after them
    text = re.split(
        r"\n\s*==\s*(?:See also|References|External links|"
        r"Further reading|Notes|Bibliography)\s*==",
        text,
        maxsplit=1,
        flags=re.IGNORECASE
    )[0]

    # Remove leftover Wikipedia markup
    text = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[https?://[^\s\]]+\s*([^\]]*)\]", r"\1", text)
    text = re.sub(r"'{2,5}", "", text)

    # Fix spacing without joining separate words
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_value(value):
    """Clean text values inside nested JSON data."""
    if isinstance(value, str):
        return clean_text(value)

    if isinstance(value, list):
        return [clean_value(item) for item in value]

    if isinstance(value, dict):
        return {key: clean_value(item) for key, item in value.items()}

    return value


def main():
    if not RAW_DATA_DIR.exists():
        logging.error("Raw data folder not found: %s", RAW_DATA_DIR)
        print("ERROR: data/raw folder was not found.")
        return

    files = list(RAW_DATA_DIR.glob("*.json"))
    cleaned = 0
    failed = 0

    print(f"Found {len(files)} company JSON files.")

    for file_path in files:
        try:
            # Read the original file without changing it
            with file_path.open("r", encoding="utf-8-sig") as file:
                original_data = json.load(file)

            cleaned_data = clean_value(original_data)

            # Save cleaned data to a separate folder
            output_dir = BASE_DIR / "data" / "cleaned"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / file_path.name

            with output_path.open("w", encoding="utf-8") as file:
                json.dump(
                    cleaned_data,
                    file,
                    ensure_ascii=False,
                    indent=2
                )

            cleaned += 1
            logging.info("Cleaned %s", file_path.name)
            print(f"Cleaned: {file_path.name}")

        except (json.JSONDecodeError, OSError, UnicodeError, TypeError) as error:
            failed += 1
            logging.exception("Could not clean %s", file_path.name)
            print(f"Failed: {file_path.name} - {error}")

    print("\nCleaning completed.")
    print(f"Successful: {cleaned}")
    print(f"Failed: {failed}")
    print(f"Cleaned files saved in: {BASE_DIR / 'data' / 'cleaned'}")
    print("Original files in data/raw have not been changed.")


if __name__ == "__main__":
    main()
