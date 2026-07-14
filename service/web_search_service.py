from ddgs import DDGS
from core.constants import constants

class WebSearchService:
    def __init__(self):
        pass

    def search(self, query: str) -> str:
        try:
            with DDGS() as ddgs:
                results = list(
                    ddgs.text(
                        query,
                        max_results=5
                    )
                )

            if not results:
                return constants.NO_RSLTS_FND

            output = []

            for index, result in enumerate(results, start=1):
                output.append(
                    f"{index}. {result[constants.TITLE]}\n"
                    f"{result[constants.BDY]}\n"
                    f"{result[constants.HREF]}"
                )
            
            return "\n\n".join(output)

        except Exception as ex:
            return f"Web search failed. {str(ex)}"
