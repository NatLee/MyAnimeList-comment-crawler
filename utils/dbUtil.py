import datetime
import sqlite3
from typing import Dict, List, Any

from loguru import logger

from tqdm import tqdm
from utils.gloVar import DATABASE_NAME

class Database(object):
    __single = None
    __db = None
    __conn = None

    def __new__(cls):
        if not Database.__single:
            Database.__db = DATABASE_NAME
            Database.__conn = sqlite3.connect(Database.__db)
            Database.__single = super(Database, cls).__new__(cls)
        return Database.__single

    def executeQuery(self, query: str, args=None):
        cursor = self.__conn.cursor()
        result = None
        try:
            if args:
                cursor.execute(query, args)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"An error occurred: {e.args[0]}")
        return result

    def databaseCommit(self):
        try:
            self.__conn.commit()
        except sqlite3.Error as e:
            logger.error(f"An error occurred: {e.args[0]}")

    def closeConnection(self):
        if self.__conn:
            self.__conn.close()


class AnimeAccess(object):
    
    def __init__(self, db: Database):
        self.__db = db
        self.__allReviewsLastPostTime = None
        self.__lastReviewPostTime = None

        self.__reviewsTableName = 'reviews'
        self.__workInfosTableName = 'animeList'

        self.initialize_tables()

    def initialize_tables(self):
        self.check_and_create_reviews_table()
        self.check_and_create_work_infos_table()

    def check_and_create_reviews_table(self):
        query = f"""
        CREATE TABLE IF NOT EXISTS "{self.__reviewsTableName}" (
            id INTEGER PRIMARY KEY,
            workId INTEGER NOT NULL,
            url TEXT,
            workName TEXT,
            postTime TEXT,
            episodesSeen INTEGER,
            overallRating INTEGER,
            author TEXT,
            reviewId INTEGER UNIQUE,
            review TEXT,
            reviewerProfileUrl TEXT,
            reviewerImageUrl TEXT,
            recommendationStatus TEXT,
            nice INTEGER,
            loveIt INTEGER,
            funny INTEGER,
            confusing INTEGER,
            informative INTEGER,
            wellWritten INTEGER,
            creative INTEGER
        )
        """
        self.__db.executeQuery(query)

    def check_and_create_work_infos_table(self):
        query = f"""CREATE TABLE IF NOT EXISTS `{self.__workInfosTableName}` (
                    `id` INTEGER PRIMARY KEY,
                    `workId` INTEGER UNIQUE,
                    `url` TEXT,
                    `jpName` TEXT,
                    `engName` TEXT,
                    `synonymsName` TEXT,
                    `workType` TEXT,
                    `episodes` INTEGER,
                    `status` TEXT,
                    `aired` TEXT,
                    `premiered` TEXT,
                    `producer` TEXT,
                    `broadcast` TEXT,
                    `licensors` TEXT,
                    `studios` TEXT,
                    `genres` TEXT,
                    `source` TEXT,
                    `duration` TEXT,
                    `rating` TEXT,
                    `score` REAL,
                    `allRank` INTEGER,
                    `popularityRank` INTEGER,
                    `members` INTEGER,
                    `favorites` INTEGER,
                    `scoredByUser` INTEGER,
                    `lastUpdate` TEXT
                    )"""

        self.__db.executeQuery(query)

    def get_all_work_id_and_review(self) -> Dict[str, List[Any]]:
        try:
            result = self.__db.executeQuery('SELECT reviewId, review FROM reviews', None)
            data = {
                'ids': [],
                'reviews': [],
                'lengths': []
            }
            for element in result:
                data['ids'].append(element['reviewId'])
                data['reviews'].append(element['review'])
                data['lengths'].append(len(element['review'].split(' ')))

            return data
        except Exception as e:
            logger.error(f"Error in get_all_work_id_and_review: {e}")
            return {}

    def get_all_work_last_review_post_time(self) -> dict:
        try:
            if self.__allReviewsLastPostTime is None:
                results = self.__db.executeQuery('SELECT workId, MAX(postTime) as postTime FROM reviews GROUP BY workId', None)
                self.__allReviewsLastPostTime = {str(result['workId']): result['postTime'] for result in results}
        except Exception as e:
            logger.error(f"Error in get_all_work_last_review_post_time: {e}")
        return self.__allReviewsLastPostTime

    def get_all_work_id(self) -> list:
        try:
            query = f'SELECT workId FROM {self.__workInfosTableName}'
            results = self.__db.executeQuery(query, None)
            return [result.get('workId') for result in results]
        except Exception as e:
            logger.error(f"Error in get_all_work_id: {e}")

    def get_all_work_urls(self) -> list:
        try:
            query = f'SELECT url FROM {self.__workInfosTableName}'
            results = self.__db.executeQuery(query, None)
            logger.info(f'URLs -> {len(results)}')
            return [url for url, *_ in results]
        except Exception as e:
            logger.error(f"Error in get_all_work_urls: {e}")

    def get_all_review_ids(self) -> List[int]:
        try:
            query = f'SELECT reviewId FROM {self.__reviewsTableName}'
            results = self.__db.executeQuery(query, None)
            return [result[0] for result in results]
        except Exception as e:
            logger.error(f"Error in get_all_review_ids: {e}")
            return []

    def review_exists(self, review_id: int) -> bool:
        try:
            query = f'SELECT reviewId FROM {self.__reviewsTableName} WHERE reviewId = ?'
            result = self.__db.executeQuery(query, (review_id,))
            return bool(result)
        except Exception as e:
            logger.error(f"Error in review_exists: {e}")
            return False

    def push_reviews_to_database(self, reviews: list):
        query = f"""INSERT OR REPLACE INTO `{self.__reviewsTableName}` 
        (`workId`, `reviewId`, `url`, `postTime`, `episodesSeen`, `author`, 
        `review`, `overallRating`, `reviewerProfileUrl`, `reviewerImageUrl`, 
        `recommendationStatus`, `nice`, `loveIt`, `funny`, `confusing`, `informative`, 
        `wellWritten`, `creative`) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        for review in reviews:
            args = (review['workId'], review['reviewId'], review['url'], review['postTime'], 
                    review['episodesSeen'], review['author'], review['review'], 
                    review['overallRating'], review['reviewerProfileUrl'], 
                    review['reviewerImageUrl'], review['recommendationStatus'], 
                    review['nice'], review['loveIt'], review['funny'], 
                    review['confusing'], review['informative'], review['wellWritten'], 
                    review['creative'])
            try:
                self.__db.executeQuery(query, args)
            except Exception as e:
                print(review)
                print(e)
                break

        self.__db.databaseCommit()

    def push_work_infos_to_database(self, workInfos: list):
        query = f"""INSERT OR REPLACE INTO `{self.__workInfosTableName}` 
        (`workId`, `url`, `jpName`, `engName`, `synonymsName`, `workType`, `episodes`, 
        `status`, `aired`, `premiered`, `producer`, `broadcast`, `licensors`, `studios`, 
        `genres`, `source`, `duration`, `rating`, `score`, `allRank`, `popularityRank`, 
        `members`, `favorites`, `scoredByUser`, `lastUpdate`) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        logger.info('Pushing anime list data to database.')
        workInfoProgress = tqdm(workInfos, ascii=True)
        for workInfo in workInfoProgress:
            workInfoProgress.set_description(f'Database Processing [{workInfo["workId"]}] {workInfo["jpName"]}')

            args = (workInfo['workId'], workInfo['url'], workInfo['jpName'], workInfo['engName'], 
                    workInfo['synonymsName'], workInfo['workType'], workInfo['episodes'], workInfo['status'], 
                    workInfo['aired'], workInfo['premiered'], workInfo['producer'], workInfo['broadcast'], 
                    workInfo['licensors'], workInfo['studios'], workInfo['genres'], workInfo['source'], 
                    workInfo['duration'], workInfo['rating'], workInfo['score'], workInfo['allRank'], 
                    workInfo['popularityRank'], workInfo['members'], workInfo['favorites'], 
                    workInfo['scoredByUser'], workInfo['lastUpdate'])

            try:
                self.__db.executeQuery(query, args)
            except Exception as e:
                print(workInfo)
                print(e)
                break

        self.__db.databaseCommit()
