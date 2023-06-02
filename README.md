# MyAnimeList Crawler

This crawler can crawl all work information and reviews from myAnimeList by using `Scrapy`.

## Usage

1. Ensure your settings in `./setting.ini`.
2. Install the required dependencies.

  ```bash
  pip install -r requirements.txt
  ```

## Usage

### Crawl Anime Infomation

  ```bash
  scrapy runspider info_spider.py --nolog
  ```

  ```json
  {
    "workId": "11979",
    "url": "https://myanimelist.net/anime/11979/Mahou_Shoujo_Madoka%E2%98%85Magica_Movie_2__Eien_no_Monogatari",
    "jpName": "劇場版 魔法少女まどか☆マギカ 永遠の物語",
    "engName": "Puella Magi Madoka Magica the Movie Part 2: Eternal",
    "synonymsName": "Mahou Shoujo Madoka Magika Movie 2, Magical Girl Madoka Magica Movie 2",
    "workType": "Movie",
    "episodes": "1",
    "status": "Finished Airing",
    "aired": "Oct 13, 2012",
    "premiered": "",
    "producer": "Aniplex, Mainichi Broadcasting System, Movic, Nitroplus, Houbunsha",
    "broadcast": "",
    "licensors": "Aniplex of America",
    "studios": "Shaft",
    "genres": "Drama",
    "source": "Original",
    "duration": "1 hr. 49 min.",
    "rating": "PG-13 - Teens 13 or older",
    "score": "8.37",
    "allRank": "#197",
    "popularityRank": "#1132",
    "members": "195,001",
    "favorites": "1,026",
    "scoredByUser": "97097",
    "lastUpdate": "2023-05-31 13:39:02"
}
  ```

### Crawl Reviews

> Need crawl information of works at first because we need the list of Anime works in `myanimelist`.

```bash
scrapy runspider review_spider.py --nolog
```

## Link

The dataset is put on [Kaggle](https://www.kaggle.com/natlee/myanimelist-comment-dataset).

