import pydantic
import re
import logging
import requests
from enum import StrEnum
from bs4 import Tag, PageElement

logger = logging.getLogger(__name__)

magnet_regex = re.compile(r'^magnet')


class TorrentInfo(pydantic.BaseModel):
    """
    Represents metadata for a torrent result.

    Attributes:
        name: The name of the torrent.
        url: The detail page URL for the torrent.
        seeders: Number of seeders.
        leechers: Number of leechers.
        size: Human-readable size of the torrent (e.g., '700 MB').
        category: Optional category the torrent belongs to.
        uploader: Optional uploader's name.
        magnet: Magnet link for the torrent.
    """
    name: str
    url: str
    seeders: int
    leechers: int
    size: str
    category: str | None = None
    uploader: str | None = None
    magnet: str | None = None


class SearchParams(pydantic.BaseModel):
    """
    Holds search parameters for querying torrents.

    Attributes:
        name: The search term (e.g., torrent name).
        category: Optional category to filter results.
        order_column: Optional column name to sort results by.
        order_ascending: Whether results should be in ascending order.
    """
    name: str
    category: StrEnum | None = None
    order_column: StrEnum | None = None
    order_ascending: bool = False


class Scraper:
    """
    Base class for torrent site scrapers.

    Designed to be subclassed for specific torrent sites by implementing
    the `parse_response`, `get_torrent_url` and `get_request_data` methods.

    Attributes:
        name: A unique identifier for the scraper (used in logs).
        base_url: Base URL of the target website.
        timeout: Timeout value for requests (can be float or tuple).
    """

    def __init__(
        self,
        name: str,
        base_url: str,
        timeout: float | tuple[float, float] = 10.0
    ):
        self.name = name
        self.base = base_url
        self.lp = f"[{self.name}]"  # log prefix
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0'
        }
        self.params = None

    def find_torrents(
        self,
        params: SearchParams,
        pages: tuple[int] = (1,),
        timeout: float | tuple[float, float] | None = None
    ) -> list[TorrentInfo]:
        """
        Searches for torrents across the specified pages.

        Args:
            params: SearchParams instance containing query filters.
            pages: Tuple of page numbers to scrape.
            timeout: Timeout value for requests (can be float, tuple or None).

        Returns:
            A list of TorrentInfo objects.
        """
        logger.info(f"{self.lp} Started")
        results = []

        self.params = params
        if timeout:
            self.timeout = timeout

        for page_number in pages:
            page_results = self.get_page_results(page_number)
            results.extend(page_results)

        logger.info(f"{self.lp} Finished")
        return results

    def get_torrent_info(
        self,
        torrent: TorrentInfo
    ) -> None:
        """
        Fetches information about single torrent.

        Args:
            torrent_url: URL of torrent detail page.
        """
        logger.info(f"{self.lp} Fetching torent info...")
        try:
            response = requests.get(torrent.url, headers=self.headers)
            response.raise_for_status()
            logger.info(f"{self.lp} Done")
            return self.parse_detail_page(response, torrent)
        except requests.Timeout:
            logger.warning(f"{self.lp} Timeout for {torrent.url}")
        except requests.ConnectionError:
            logger.warning(f"{self.lp} Connection error for {torrent.url}")
        return None

    def get_torrent_url(self, url):
        """
        Constructs the full torrent URL from a relative path.

        Args:
            url: Relative URL string.

        Returns:
            Full URL string.
        """
        return f"{self.base}{url}"

    def get_page_results(
        self,
        page_number: int,
    ) -> list[TorrentInfo]:
        """
        Fetches and parses a single page of torrent results.

        Args:
            page_number: The page number to fetch.

        Returns:
            A list of TorrentInfo objects parsed from the page.
        """
        logger.info(f"{self.lp} Fetching page {page_number}")
        url, payload = self.get_request_data(page_number)
        results = []

        try:
            response = requests.get(url, params=payload, headers=self.headers,
                                    timeout=self.timeout)
            response.raise_for_status()
            results = self.parse_search_page(response)
        except requests.Timeout:
            logger.warning(f"{self.lp} Timeout for {url}")
        except requests.ConnectionError:
            logger.warning(f"{self.lp} Connection error for {url}")

        return results

    def get_request_data(
        self,
        page_number: int,
    ) -> tuple[str, dict]:
        """
        Returns the URL and payload parameters for the HTTP GET request.

        This method should be overridden for site-specific parameters.

        Args:
            page_number: The page number to fetch.

        Returns:
            A tuple of (URL, payload dict).
        """
        return (self.base, {})

    def parse_search_page(
        self,
        response: requests.Response
    ) -> list[TorrentInfo]:
        """
        Parses the HTTP response and extracts torrent information.

        Must be implemented by subclasses.

        Returns:
            A list of TorrentInfo objects.
        """
        raise NotImplementedError(
            "Subclasses must implement `parse_search_page`"
        )

    def parse_detail_page(
        self,
        response: requests.Response,
        torrent: TorrentInfo
    ) -> TorrentInfo:
        """
        Parses the HTTP response and extracts torrent information.

        Must be implemented by subclasses.

        Returns:
            A list of TorrentInfo objects.
        """
        raise NotImplementedError(
            "Subclasses must implement `parse_detail_page`"
        )

    def find_all(
        self,
        source: Tag,
        name: str,
        recursive: bool = True,
        **kwargs
    ) -> list[PageElement]:
        """
        Utility to find all matching HTML elements.

        Logs a warning if no elements are found.

        Returns:
            A list of matching PageElements.
        """
        items = source(name, recursive=recursive, **kwargs)
        if not items:
            logger.warning(f"{self.lp} {name} not found on page")
        return items

    def find_element(
        self,
        source: Tag,
        name: str,
        recursive: bool = True,
        **kwargs
    ) -> PageElement | None:
        """
        Utility to find a single HTML element.

        Logs a warning if the element is not found.

        Returns:
            A matching PageElement or None.
        """
        el = source.find(name, recursive=recursive, **kwargs)
        if not el:
            logger.warning(f"{self.lp} {name} not found on page")
        return el
