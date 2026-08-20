from ddgs import DDGS
from bs4 import BeautifulSoup
import requests

from core.constants import constants


class WebSearchService:

    MAX_RESULTS = 5
    MAX_PAGES = 3
    MAX_CONTENT_PER_PAGE = 3000
    MAX_TOTAL_CONTENT = 8000
    TIMEOUT = 8

    def search(self, query: str) -> dict:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query,max_results=self.MAX_RESULTS))

            if not results:
                return {
                    constants.SUMMARY: constants.NO_RSLTS_FND,
                    constants.CITATIONS: [],
                    constants.METADATA: {},
                }

            citations = []
            sources = []
            total_content = 0

            for index, result in enumerate(results[:self.MAX_PAGES],1):
                title = result.get(constants.TITLE,constants.EMPTY_STRING)
                url = result.get(constants.HREF,constants.EMPTY_STRING)
                snippet = result.get(constants.BDY,constants.EMPTY_STRING)
                citations.append({constants.TITLE: title,constants.URL: url,})

                remaining = (self.MAX_TOTAL_CONTENT - total_content)
                if remaining <= 0:
                    break

                content = self._fetch(url)
                if not content:
                    content = snippet
                content = content[:min(self.MAX_CONTENT_PER_PAGE,remaining)]

                total_content += len(content)

                if content:
                    sources.append(
                        f"Source {index}: {title}\n"
                        f"URL: {url}\n"
                        f"Content:\n{content}"
                    )

            summary = "\n\n---\n\n".join(sources)

            return {
                constants.SUMMARY: summary,
                constants.CITATIONS: citations,
                constants.METADATA: {
                    constants.QUERY: query,
                    "result_count": len(results),
                },
            }

        except Exception as ex:
            return {
                constants.SUMMARY:
                    f"Web search failed: {str(ex)}",
                constants.CITATIONS: [],
                constants.METADATA: {},
            }

    def _fetch(self, url: str) -> str:
        try:
            response = requests.get(
                url,
                timeout=self.TIMEOUT,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "(Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 "
                        "(KHTML, like Gecko) "
                        "Chrome/151.0.0.0 Safari/537.36"
                    )
                },
            )

            response.raise_for_status()
            soup = BeautifulSoup(response.text, constants.HTML_PARSER)
            for tag in soup([constants.BS4_SOUP]):
                tag.decompose()

            return soup.get_text(" ",strip=True)
        except Exception:
            return constants.EMPTY_STRING
