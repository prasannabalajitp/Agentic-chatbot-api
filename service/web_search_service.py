from ddgs import DDGS
from bs4 import BeautifulSoup
import requests
import logging

from core.constants import constants

logger = logging.getLogger(__name__)


class WebSearchService:

    MAX_RESULTS = 5
    MAX_PAGES = 3
    MAX_CONTENT_PER_PAGE = 1000
    MAX_TOTAL_CONTENT = 3000
    TIMEOUT = 8

    def search(self, query: str) -> dict:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query,max_results=self.MAX_RESULTS))

            if not results:
                return {
                    constants.SUMMARY: constants.NO_RSLTS_FND,
                    constants.CITATIONS: [],
                    constants.METADATA: {
                        constants.SUCC: True,
                        constants.QUERY: query,
                        constants.RESULT_CNT: 0,
                    }
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

            logger.info(
                "WEB SEARCH RESULT METADATA: %s",
                {
                    constants.SUCC: True,
                    constants.QUERY: query,
                    constants.RESULT_CNT: len(results),
                },
            )

            result = {
                constants.SUMMARY: summary,
                constants.CITATIONS: citations,
                constants.METADATA: {
                    constants.SUCC: True,
                    constants.QUERY: query,
                    constants.RESULT_CNT: len(results),
                },
            }

            return result

        except (TimeoutError, requests.Timeout):
            logger.exception("Web search timeout | query=%s", query)

            return {
                constants.SUMMARY: "Web search timed out.",
                constants.CITATIONS: [],
                constants.METADATA: {
                    constants.SUCC: False,
                    constants.ERROR_TYPE: constants.TIMEOUT,
                    constants.RETRYABLE: True,
                },
            }

        except requests.HTTPError as ex: 
            status_code = ex.response.status_code if ex.response else None
            if status_code == 429:
                logger.exception("Web search rate limited | query=%s", query)

                return {
                    constants.SUMMARY: "Web search is temporarily rate limited.",
                    constants.CITATIONS: [],
                    constants.METADATA: {
                        constants.SUCC: False,
                        constants.ERROR_TYPE: constants.RATE_LIMIT,
                        constants.RETRYABLE: True,
                    },
                }

            if status_code and 500 <= status_code < 600:
                logger.exception("Web search service error | query=%s | status=%s", query, status_code)
                return {
                    constants.SUMMARY: "Web search service is temporarily unavailable.",
                    constants.CITATIONS: [],
                    constants.METADATA: {
                        constants.SUCC: False,
                        constants.ERROR_TYPE: constants.SERVICE_ERROR,
                        constants.RETRYABLE: True,
                    },
                }

            raise

        except Exception as ex:
            logger.exception("Web search failed | query=%s", query)

            return {
                constants.SUMMARY: "Web search temporarily failed.",
                constants.CITATIONS: [],
                constants.METADATA: {
                    constants.SUCC: False,
                    constants.ERROR_TYPE: constants.UNKNOWN_ERROR,
                    constants.RETRYABLE: False,
                },
            }

    def _fetch(self, url: str) -> str:
        try:
            response = requests.get(
                url,
                timeout=self.TIMEOUT,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0"
                    )
                },
            )

            response.raise_for_status()
            soup = BeautifulSoup(response.text, constants.HTML_PARSER)
            for tag in soup(constants.BS4_SOUP):
                tag.decompose()

            content = (soup.find(constants.ARTICLE) or soup.find(constants.MAIN) or soup.body or soup)
            text = content.get_text(" ",strip=True)
            text = " ".join(text.split())
            return text
        except Exception:
            return constants.EMPTY_STRING
