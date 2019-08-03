
# myAnimeList Comment and Work Information Crawler

This crawler can crawl all work information and comments from myAnimeList by sending request.

## Steps 
----------

**!!DO NOT SET TOO MANY PROCESSES, YOU WILL BE BANNED!!**

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

## Commands 
-----------

You need to create database and table with sql below in the first.

```sql

CREATE DATABASE IF NOT EXISTS `anime`;

DROP TABLE IF EXISTS `animeList`;
CREATE TABLE `animeList` (
  `id` int(16) unsigned NOT NULL AUTO_INCREMENT,
  `workId` int(16) unsigned DEFAULT NULL,
  `workName` varchar(128) DEFAULT NULL,
  `engName` varchar(128) DEFAULT NULL,
  `synonymsName` varchar(256) DEFAULT NULL,
  `jpName` varchar(128) DEFAULT NULL,
  `workType` varchar(16) DEFAULT NULL,
  `episodes` int(4) DEFAULT NULL,
  `status` varchar(64) DEFAULT NULL,
  `aired` varchar(64) DEFAULT NULL,
  `permiered` varchar(32) DEFAULT NULL,
  `broadcast` varchar(64) DEFAULT NULL,
  `producer` text DEFAULT NULL,
  `licensors` text DEFAULT NULL,
  `studios` text DEFAULT NULL,
  `source` varchar(128) DEFAULT NULL,
  `genres` text DEFAULT NULL,
  `duration` varchar(64) DEFAULT NULL,
  `rating` varchar(64) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `scoredByUser` int(16) DEFAULT NULL,
  `allRank` int(16) unsigned DEFAULT NULL,
  `popularityRank` int(16) unsigned DEFAULT NULL,
  `members` int(16) unsigned DEFAULT NULL,
  `favorities` int(16) unsigned DEFAULT NULL,
  `lastUpdate` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_index` (`workId`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `reviews`;
CREATE TABLE `reviews` (
  `id` int(16) unsigned NOT NULL AUTO_INCREMENT,
  `workId` int(16) unsigned DEFAULT NULL,
  `reviewId` int(16) unsigned DEFAULT NULL,
  `workName` varchar(128) DEFAULT NULL,
  `postTime` datetime DEFAULT NULL,
  `episodesSeen` int(4) DEFAULT NULL,
  `author` varchar(64) DEFAULT NULL,
  `peopleFoundUseful` int(8) unsigned DEFAULT NULL,
  `review` text DEFAULT NULL,
  `overallRating` int(2) DEFAULT NULL,
  `storyRating` int(2) DEFAULT NULL,
  `animationRating` int(2) DEFAULT NULL,
  `soundRating` int(2) DEFAULT NULL,
  `characterRating` int(2) DEFAULT NULL,
  `enjoymentRating` int(2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_index` (`reviewId`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4;

```

## Link

This dataset is put on [Kaggle](https://www.kaggle.com/natlee/myanimelist-comment-dataset).

