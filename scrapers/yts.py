from urllib.parse import quote_plus
from scrapers import Scraper, SearchParams, TorrentInfo
from enum import StrEnum


class CategoryYTS(StrEnum):
    ALL = "all"
    ACTION = "action"
    ADVENTURE = "adventure"
    ANIMATION = "animation"
    BIOGRAPHY = "biography"
    COMEDY = "comedy"
    CRIME = "crime"
    DOCUMENTARY = "documentary"
    DRAMA = "drama"
    FAMILY = "family"
    FANTASY = "fantasy"
    FILM_NOIR = "film-noir"
    GAME_SHOW = "game-show"
    HISTORY = "history"
    HORROR = "horror"
    MUSIC = "music"
    MUSICAL = "musical"
    MYSTERY = "mystery"
    NEWS = "news"
    REALITY_TV = "reality-tv"
    ROMANCE = "romance"
    SCI_FI = "sci-fi"
    SPORT = "sport"
    TALK_SHOW = "talk-show"
    THRILLER = "thriller"
    WAR = "war"
    WESTERN = "western"


class OrderYTS(StrEnum):
    TITLE = 'title'
    YEAR = 'year'
    RATING = 'rating'
    LEECHERS = 'peers'
    SEEDERS = 'seeds'
    DOWNLOADS = 'download_count'
    LIKES = 'like_count'
    DATE = 'date_added'


class QualityYTS(StrEnum):
    ALL = 'all'
    Q480 = '480p'
    Q720 = '720p'
    Q1080 = '1080p'
    Q1080_X265 = '1080p.x265'
    Q2160 = '2160p'
    Q3D = '3D'


class ParamsYTS(SearchParams):
    category: CategoryYTS = CategoryYTS.ALL
    order_column: OrderYTS = OrderYTS.DATE
    quality: QualityYTS = QualityYTS.ALL
    minimum_rating: int = 0
    limit: int = 50


_trackers = "&tr=".join([
    'udp://open.demonii.com:1337/announce',
    'udp://tracker.openbittorrent.com:80',
    'udp://tracker.coppersurfer.tk:6969',
    'udp://glotorrents.pw:6969/announce',
    'udp://tracker.opentrackr.org:1337/announce',
    'udp://torrent.gresille.org:80/announce',
    'udp://p4p.arenabg.com:1337',
    'udp://tracker.leechers-paradise.org:6969',
])
_quality_values = [q.value for q in QualityYTS]


class ScraperYTS(Scraper):
    def __init__(self):
        super().__init__(
            'YTS.mx',
            'https://yts.mx/api/v2',
        )
        self.headers = {}

    def get_request_data(self, page: int):
        params = self.params
        payload = {
            "limit": params.limit,
            "page": page,
            "quality": params.quality.value,
            "minimum_rating": params.minimum_rating,
            "query_term": quote_plus(params.name),
            "genre": params.category.value,
            "sort_by": params.order_column.value,
            "order_by": "asc" if params.order_ascending else "desc"
        }

        return f"{self.base}/list_movies.json", payload

    def parse_search_page(self, response) -> list[TorrentInfo]:
        """
        Parses the Nyaa.si search results page and extracts torrent info.

        Returns:
            A list of TorrentInfo objects.
        """
        results = []
        json = response.json()
        if json["status"] == "ok":
            data = json['data']
            if data['movie_count']:
                movies = data['movies']
                for item in movies:
                    torrent_data = {
                        "url": str(item['id']),
                        "name": item['title']
                    }
                    if item['genres']:
                        torrent_data['category'] = item['genres'][0]
                    if torrents := item['torrents']:
                        tor = None
                        if self.params.quality != QualityYTS.ALL:
                            for t in torrents:
                                if t['quality'] in _quality_values:
                                    tor = t
                        else:
                            tor = torrents[0]
                        torrent_data['seeders'] = tor['seeds']
                        torrent_data['leechers'] = tor['peers']
                        torrent_data['size'] = tor['size']
                        torrent_data['magnet'] = self.get_magnet_link(tor, item['title'])
                    results.append(TorrentInfo(**torrent_data))
        return results

    def get_magnet_link(self, torrent: dict, name: str):
        name_enc = quote_plus(name)
        hash = torrent['hash']
        return f"magnet:?xt=urn:btih:{hash}&dn={name_enc}&tr={_trackers}"
