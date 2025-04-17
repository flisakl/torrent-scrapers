# Torrent Scraper Collection

Collection of web scrapers of popular torrent sites.

Currently package provides scrapers for:
- [1337x](https://1337x.to)
- [Nyaa](https://nyaa.si)
- [YTS YIFY](https://yts.mx)

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
pip install torrent-scrapers
```

### Manual installation

🧱 Requirements

- Python 3.10+
- `requests`
- `beautifulsoup4`
- `pydantic`

#### Clone repository

```bash
git clone https://github.com/flisakl/torrent-scrapers
cd torrent-scrapers
```

#### Install dependencies

```bash
pip install requests beautifulsoup4 pydantic
```

## 🛠 Usage

### Using built in scraper
```python
from scrapers.x1337 import Scraper1337, Params1337, Category1337, Order1337

scraper = Scraper1337()

params = Params1337(
    name="ozark",
    category=Category1337.TV,
    order_column=Order1337.SIZE,
    order_ascending=False
)

results = scraper.find_torrents(params, (1,))

for torrent in results:
    scraper.get_torrent_info(torrent)
    print(torrent)
```

### 🧩 Making your own scraper

To add support for a new torrent site:

1. Subclass Scrapper
1. Implement the following methods:
    - get_request_data
    - parse_search_page
    - parse_detail_page


### 🔧 Structures

#### TorrentInfo

Pydantic's model containing torrent informations.

| **Field** | **Type** | **Description**                   |
|-----------|----------|-----------------------------------|
| name      | str      | Search term                       |
| url       | str      | URL for torrent detail page       |
| seeders   | int      | Number of seeders                 |
| leechers  | int      | Number of leechers                |
| size      | str      | Size of torrent's data            |
| magnet    | str      | Magnet link                       |
| uploader  | str      | Optional name of torrent uploader |
| category  | str      | Optional category of the torrent  |

#### SearchParams

Pydantic's model containing search parameters, it is best to create subclass
for each scraper.

| **Field**       | **Type** | **Description**            |
|-----------------|----------|----------------------------|
| name            | str      | Search term                |
| category        | str      | Optional category          |
| order_column    | str      | Optional sorting column    |
| order_ascending | bool     | Sort order                 |
