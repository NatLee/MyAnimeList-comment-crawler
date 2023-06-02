<div align="center" style="text-align: center">

<p style="text-align: center">
  <img align="center" src="https://camo.githubusercontent.com/40d00cefb120a829517e503658aaf6c987d5f9cc6be5e2e35fb20bd63bdbceb5/68747470733a2f2f7363726170792e6f72672f696d672f7363726170796c6f676f2e706e67" width="30%" height="100%">
  <img align="center" src="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png" width="10%" height="100%">
</p>

# MyAnimeList Crawler
This crawler can crawl all work information and reviews from `MyAnimeList` by using `Scrapy`.

</div>


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

- Example of crawling data
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

You can obtain the data from your SQLite database by using the following command.
```bash
python db_to_kaggle.py
```

## Misc

I recommend using [VisiData](https://www.visidata.org/) to see the SQLite database and the CSV files.

![](https://d33wubrfki0l68.cloudfront.net/a2039fda848c76b90ee0270854cd417a82bbd60e/0b350/img/woq9dm5llq-590.webp)

It can see details of the structured data in CLI.

Just use `sudo apt install VisiData` to get the package.

In our case, you can use `vd anime.db` to get a view with the SQLite database.

## Contributor

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center"><a href="https://github.com/NatLee"><img src="https://avatars.githubusercontent.com/u/10178964?v=3?s=100" width="100px;" alt="Nat Lee"/><br /><sub><b>Nat Lee</b></sub></a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## LICENSE

[MIT](LICENSE)


