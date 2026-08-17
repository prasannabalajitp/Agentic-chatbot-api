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
                    "summary": constants.NO_RSLTS_FND,
                    "citations": [],
                    "metadata": {},
                }

            citations = []
            summary = []

            for i, r in enumerate(results, 1):
                citations.append({
                    constants.TITLE: r[constants.TITLE],
                    constants.URL: r[constants.HREF],
                })

                summary.append(
                    f"{i}. {r['title']}\n"
                    f"{r['body']}"
                )
            
            data = {
                "summary": "\n\n".join(summary),
                "citations": citations,
                "metadata": {},
            }
            return data

        except Exception as ex:
            return {
                "summary": f"Web search failed. {ex}",
                "citations": [],
                "metadata": {},
            }
