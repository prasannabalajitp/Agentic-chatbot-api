from ddgs import DDGS
from core.constants import constants

class WebSearchService:
    def __init__(self):
        pass

    def search(self, query: str) -> dict:
        try:
            with DDGS() as ddgs:
                results = list(
                    ddgs.text(
                        query,
                        max_results=5
                    )
                )

            if not results:
                return {
                    constants.CNTXT: constants.NO_RSLTS_FND,
                    constants.CITATIONS: []
                }

            citations = []
            context = []

            for i, r in enumerate(results, 1):
                citations.append({
                    constants.TITLE: r[constants.TITLE],
                    constants.URL: r[constants.HREF],
                })

                context.append(
                    f"{i}. {r['title']}\n"
                    f"{r['body']}\n"
                    f"Source: {r['href']}"
                )
            
            data = {
                constants.CNTXT: "\n\n".join(context),
                constants.CITATIONS: citations,
            }
            return data

        except Exception as ex:
            return {
                constants.CNTXT: f"Web search failed. {ex}",
                constants.CITATIONS: [],
            }
