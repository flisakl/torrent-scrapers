from scrapers import Scraper, SearchParams, TorrentInfo, magnet_regex
from bs4 import BeautifulSoup
from enum import StrEnum


class CategoryNya(StrEnum):
    ALL = '0_0'
    ANIME = '1_0'
    ANIME_MUSIC_VIDEO = '1_1'
    ANIME_ENGLISH = '1_2'
    ANIME_NON_ENGLISH = '1_3'
    ANIME_RAW = '1_4'
    AUDIO = '2_0'
    AUDIO_LOSSLESS = '2_1'
    AUDIO_LOSSY = '2_2'
    LITERATURE = '3_0'
    LITERATURE_ENGLISH = '3_1'
    LITERATURE_NON_ENGLISH = '3_2'
    LITERATURE_RAW = '3_3'
    LIVE_ACTION = '4_0'
    LIVE_ACTION_ENGLISH = '4_1'
    LIVE_ACTION_IDOL = '4_2'
    LIVE_ACTION_NON_ENGLISH = '4_3'
    LIVE_ACTION_RAW = '4_4'
    PICTURES = '5_0'
    PICTURES_GRAPHICS = '5_1'
    PICTURES_PHOTOS = '5_2'
    SOFTWARE = '6_0'
    SOFTWARE_APPLICATIONS = '6_1'
    SOFTWARE_GAMES = '6_2'


class OrderNya(StrEnum):
    SIZE = 'size'
    DATE = 'id'
    SEEDERS = 'seeders'
    LEECHERS = 'leechers'
    DOWNLOADS = 'downloads'


class FilterNya(StrEnum):
    NO = '0'
    NO_REMAKES = '1'
    TRUSTED_ONLY = '2'


class ParamsNya(SearchParams):
    filter: FilterNya = FilterNya.NO
    category: CategoryNya = CategoryNya.ALL
    order_column: OrderNya | None = None


class ScraperNya(Scraper):
    def __init__(self):
        super().__init__(
            'Nyaa.si',
            'https://nyaa.si',
        )

    def get_request_data(self, page: int):
        params = self.params
        payload = {
            "p": page,
            "q": params.name,
            "c": params.category.value,
            "f": params.filter.value
        }
        oc = params.order_column

        if oc:
            payload["s"] = oc
            payload["o"] = "asc" if params.order_ascending else "desc"

        return f"{self.base}/", payload

    def parse_search_page(self, response) -> list[TorrentInfo]:
        """
        Parses the Nyaa.si search results page and extracts torrent info.

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

    def _parse_row(self, row) -> TorrentInfo | None:
        """
        Parses a table row and returns a TorrentInfo object if successful.

        Args:
            row: A <tr> tag containing torrent data.

        Returns:
            TorrentInfo or None.
        """
        data = {}
        row_data = self.find_all(row, "td", recursive=False)
        if row_data:
            category, name, links, size, _, se, le, _ = row_data
            data['category'] = self.find_element(
                category, 'a', recursive=False).attrs['title']
            name = self.find_all(name, 'a', recursive=False)
            if len(name) == 2:
                name = name[1]
            else:
                name = name[0]
            data['name'] = name.attrs['title']
            data['url'] = self.get_torrent_url(name.attrs['href'])
            data['size'] = size.get_text()
            data['seeders'] = int(se.get_text().strip())
            data['leechers'] = int(le.get_text().strip())
            data['magnet'] = self.find_element(
                links, 'a', href=magnet_regex).attrs['href']

            return TorrentInfo(**data)
        return None
