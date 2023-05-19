
> Notice that MyAnimeList has already updated their website, so I'm now working on the new version of this crawler.

# MyAnimeList Crawler

This crawler can crawl all work information and comments from myAnimeList by sending request.

## Steps 
----------

> **DO NOT SET TOO MANY PROCESSES, YOU WILL BE BANNED !!**

1. Check your database information in the file `setting.ini`. I suggest you can use Docker to build a [mariaDB](https://hub.docker.com/_/mariadb).
2. If you have not create database, you need to create and ensure that it can be accessed.
3. Install the packages with `pip install -r requirements.txt`
4. You can follow the help shown as following in your shell. The sample for first run, `python main.py --updateDataByWork`.

```
usage: main.py [-h] [--updateByAllReviewPage [UPDATEBYALLREVIEWPAGE]]
               [--updateDataByWork [UPDATEDATABYWORK]]

Dataset parse.

optional arguments:
  -h, --help            show this help message and exit
  --updateByAllReviewPage [UPDATEBYALLREVIEWPAGE]
                        Update database by crawling all review page. (Fast)
  --updateDataByWork [UPDATEDATABYWORK]
                        Update database by crawling review page for each work.
                        (Slow)
```

## Link

This dataset is put on [Kaggle](https://www.kaggle.com/natlee/myanimelist-comment-dataset).

