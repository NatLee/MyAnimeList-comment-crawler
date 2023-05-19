
> Notice that MyAnimeList has already updated their website, so I'm now working on the new version of this crawler.

# MyAnimeList Crawler

This crawler can crawl all work information and comments from myAnimeList by sending request.

## Quick Start

> **DO NOT SET TOO MANY PROCESSES, YOU WILL BE BANNED !!**

1. Ensure your settings in `./setting.ini`.
2. Install the required dependencies.

  ```bash
  pip install -r requirements.txt
  ```

3. Run this crawler with the following command:

  ```bash
  python main.py --updateByAllReviewPage
  ```

## Usage

```bash
python main.py --help
```

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

The dataset is put on [Kaggle](https://www.kaggle.com/natlee/myanimelist-comment-dataset).

