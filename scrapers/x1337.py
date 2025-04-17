import requests
from urllib.parse import quote_plus
from scrapers import Scraper, SearchParams, TorrentInfo, magnet_regex
from bs4 import BeautifulSoup
from enum import StrEnum


class Category1337(StrEnum):
    MOVIES = 'Movies'
    TV = 'TV'
    GAMES = 'Games'
    MUSIC = 'Music'
    APPS = 'Apps'
    DOCUMENTARIES = 'Documentaries'
    ANIME = 'Anime'
    OTHER = 'Other'
    XXX = 'XXX'


class Order1337(StrEnum):
    TIME = 'time'
    SIZE = 'size'
    SEEDERS = 'seeders'
    LEECHERS = 'leechers'


class Params1337(SearchParams):
    category: Category1337 | None = None
    order_column: Order1337 | None = None


class Scraper1337(Scraper):
    """
    A scraper implementation for 1337x.to.
    """

    def __init__(self):
        super().__init__(
            "1337x.to", 'https://1337x.to',
        )

    def get_request_data(
        self,
        page_number: int,
    ):
        """
        Constructs the request URL and parameters based on search params.

        Returns:
            A tuple of URL string and empty parameter dict.
        """
        url = self.base

        if self.params.order_column:
            dir = "asc" if self.params.order_ascending else "desc"
            order = f'{self.params.order_column.value}/{dir}'
        else:
            order = False

        category = self.params.category
        name = quote_plus(self.params.name)

        category = category.value if category else False

        if order and category:
            url += f"/sort-category-search/{name}/{category}/{order}"
        elif category:
            url += f"/category-search/{name}/{category}"
        elif order:
            url += f"/sort-search/{name}/{order}"
        else:
            url += f"/search/{name}"

        url = f"{url}/{page_number}/", {}
        return url

    def parse_search_page(self, response) -> list[TorrentInfo]:
        """
        Parses the 1337x search results page and extracts torrent info.

        Returns:
            A list of TorrentInfo objects.
        """
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        body = soup.body
        table_body = self.find_element(body, "tbody", recursive=True)

        if table_body:
            rows = self.find_all(table_body, "tr", recursive=False)
            for row in rows:
                data = self._parse_row(row)
                if data:
                    results.append(data)

        return results

    def parse_detail_page(self, response, torrent) -> TorrentInfo:
        """
        Parses torrent's detail page and updates TorrentInfo

        Args:
            torrent: A TorrentInfo object.
        """
        response = requests.get(
            torrent.url, headers=self.headers, timeout=self.timeout
        )
        body = BeautifulSoup(response.text, 'html.parser').body.find('main')
        magnet_links = self.find_all(
            body,
            'a',
            href=magnet_regex
        )

        if magnet_links:
            torrent.magnet = magnet_links[0].attrs['href']

        boxinfo = self.find_element(body, "div", class_="box-info")
        if boxinfo:
            box_lists = self.find_all(boxinfo, "ul", class_="list")
            if box_lists:
                l1, l2 = box_lists
                cat = self.find_element(l1, 'li', recursive=False)
                torrent.category = self.find_element(cat, 'span').get_text()
        return torrent

    def _parse_row(self, row) -> TorrentInfo | None:
        """
        Parses a table row and returns a TorrentInfo object if successful.

        Args:
            row: A <tr> tag containing torrent data.

        Returns:
            TorrentInfo or None.
        """
        data = {}
        row_data = self.find_all(row, "td")
        if row_data:
            name, seeds, leech, _, size, uploader = row_data

            tmp = self.find_all(name, "a")
            if tmp:
                tmp = tmp[1]
                data["name"] = tmp.string
                data["url"] = self.get_torrent_url(tmp.attrs['href'])
            data["seeders"] = int(seeds.string.strip())
            data["leechers"] = int(leech.string.strip())
            data["size"] = size.contents[0].replace(',', '')
            data["uploader"] = uploader.find("a").string
            return TorrentInfo(**data)
        return None
