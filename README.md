# Torrent Scraper Collection

Collection of web scrappers of popular torrent sites.

Currently package provides scrappers for:
- [X] [1337x](https://1337x.to)
- [ ] [The Pirate Bay](https://thepiratebay.org/index.html)

---

## 🚀 Features

- Scrape torrent listings (name, seeders, leechers, size, uploader, etc.)
- Fetch magnet links
- Handle pagination and search filters (category, sorting)
- Easily extendable to other torrent sites
- Logs warnings for missing data, connection errors and timeouts


## Installation

You can install the package from pypi or clone the repository.

### Package

```bash
pip install torrent-scrappers
```

### Manual installation

🧱 Requirements

- Python 3.10+
- `requests`
- `beautifulsoup4`

#### Clone repository

```bash
git clone https://github.com/flisakl/torrent-scrappers
cd torrent-scrappers
```

#### Install dependencies

```bash
pip install requests beautifulsoup4
```

## 🛠 Usage

### Using built in scrapper
```python
from scrappers import Scrapper1337, SearchParams

scraper = Scrapper1337()

params = SearchParams(
    name="ubuntu",
    order_column="seeders",
    order_ascending=False
)

results = scraper.find_torrents(params, pages=(1, 2))
scraper.get_magnet_links(results)

for torrent in results:
    print(torrent.name, torrent.magnet)

```

### 🧩 Making your own scrapper

To add support for a new torrent site:

1. Subclass Scrapper
1. Implement the following methods:
    - get_request_data
    - parse_response
    - fetch_magnet_link - implement when magnet link can not be obtained on site's
    search page


### 🔧 Structures

#### TorrentInfo

Dataclass containing torrent informations

| **Field** | **Type** | **Description**                   |
|-----------|----------|-----------------------------------|
| name      | str      | Search term                       |
| url       | str      | URL for torrent detail page       |
| seeders   | int      | Number of seeders                 |
| leechers  | int      | Number of leechers                |
| size      | str      | Size of torrent's data            |
| uploader  | str      | Optional name of torrent uploader |
| magnet    | str      | Magnet link                       |

#### SearchParams

Immutable dataclass for filters

| **Field**       | **Type** | **Description**   |
|-----------------|----------|-------------------|
| name            | str      | Search term       |
| category        | str      | Optional category |
| order_column    | str      | Sorting column    |
| order_ascending | bool     | Sort order        |

If **order_column** is set to None, ordering will not be applied.
