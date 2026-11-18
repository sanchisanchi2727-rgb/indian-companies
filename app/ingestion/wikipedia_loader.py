
import wikipedia


class WikipediaLoader:
    def __init__(self):
        wikipedia.set_lang("en")

    def load_company(self, company_name):
        try:
            page = wikipedia.page(
                company_name,
                auto_suggest=True,
                redirect=True
            )
            return page.content

        except wikipedia.DisambiguationError as error:
            # Try the first suggested matching page.
            for option in error.options:
                try:
                    page = wikipedia.page(
                        option,
                        auto_suggest=False,
                        redirect=True
                    )
                    return page.content
                except Exception:
                    continue

            print(f"No matching Wikipedia page for {company_name}")
            return None

        except wikipedia.PageError:
            print(f"Wikipedia page not found: {company_name}")
            return None

        except Exception as error:
            print(f"Error loading {company_name}: {error}")
            return None
