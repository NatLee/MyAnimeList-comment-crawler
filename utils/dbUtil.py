import datetime
import sqlite3

from loguru import logger

from tqdm import tqdm
from utils.gloVar import DATABASE_NAME

class Database(object):
    __single = None
    def __new__(clz):
        if not Database.__single:
            Database.__db = DATABASE_NAME
            conn = sqlite3.connect(Database.__db)
            Database.__conn = conn
            Database.__single = object.__new__(clz)
        return Database.__single

    def __getConnection(self):
        return self.__conn

    def getConnection(self):
        return self.__getConnection()

    def executeQuery(self, query: str, args=None):
        cursor = self.__conn.cursor()
        if args:
            cursor.execute(query, args)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def databaseCommit(self):
        return self.__conn.commit()


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
        query = f"CREATE TABLE IF NOT EXISTS `{self.__reviewsTableName}` (" \
                "`id` INT AUTO_INCREMENT PRIMARY KEY," \
                "`workId` INT NOT NULL," \
                "`workName` VARCHAR(255)," \
                "`postTime` TIMESTAMP," \
                "`episodesSeen` INT," \
                "`author` VARCHAR(255)," \
                "`peopleFoundUseful` INT," \
                "`reviewId` INT UNIQUE," \
                "`review` TEXT," \
                "`overallRating` INT," \
                "`storyRating` INT," \
                "`animationRating` INT," \
                "`soundRating` INT," \
                "`characterRating` INT," \
                "`enjoymentRating` INT" \
                ")"

        self.__db.executeQuery(query)

    def check_and_create_work_infos_table(self):
        query = f"CREATE TABLE IF NOT EXISTS `{self.__workInfosTableName}` (" \
                "`id` INT AUTO_INCREMENT PRIMARY KEY," \
                "`workId` INT UNIQUE," \
                "`workName` VARCHAR(255)," \
                "`engName` VARCHAR(255)," \
                "`synonymsName` VARCHAR(255)," \
                "`jpName` VARCHAR(255)," \
                "`workType` VARCHAR(255)," \
                "`episodes` INT," \
                "`status` VARCHAR(255)," \
                "`aired` VARCHAR(255)," \
                "`premiered` VARCHAR(255)," \
                "`broadcast` VARCHAR(255)," \
                "`producer` VARCHAR(255)," \
                "`licensors` VARCHAR(255)," \
                "`studios` VARCHAR(255)," \
                "`source` VARCHAR(255)," \
                "`genres` VARCHAR(255)," \
                "`duration` VARCHAR(255)," \
                "`rating` VARCHAR(255)," \
                "`score` FLOAT," \
                "`scoredByUser` INT," \
                "`allRank` INT," \
                "`popularityRank` INT," \
                "`members` INT," \
                "`favorites` INT," \
                "`lastUpdate` TIMESTAMP" \
                ")"

        self.__db.executeQuery(query)

    def get_all_work_id_and_review(self) -> dict:
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

    def get_all_work_last_review_post_time(self) -> dict:
        if self.__allReviewsLastPostTime is None:
            results = self.__db.executeQuery('SELECT workId, MAX(postTime) as postTime FROM reviews GROUP BY workId', None)
            self.__allReviewsLastPostTime = {str(result['workId']): result['postTime'] for result in results}

        return self.__allReviewsLastPostTime

    def get_all_work_id(self) -> list:
        query = f'SELECT workId FROM {self.__workInfosTableName}'
        results = self.__db.executeQuery(query, None)
        return [result.get('workId') for result in results]

    def get_last_review_post_time(self) -> dict:
        if self.__lastReviewPostTime is None:
            results = self.__db.executeQuery('SELECT workId, postTime FROM reviews ORDER BY postTime DESC LIMIT 1', None)
            if results:
                self.__lastReviewPostTime = results[0]
            else:
                self.__lastReviewPostTime ={
                    'postTime':datetime.datetime(year=1900, month=1, day=1)
                }
        return self.__lastReviewPostTime

    def push_reviews_to_database(self, reviews: list):
        query = f"INSERT INTO `{self.__reviewsTableName}` (`id`, `workId`, `workName`, `postTime`, `episodesSeen`, `author`, `peopleFoundUseful`, `reviewId`, `review`, `overallRating`, `storyRating`, `animationRating`, `soundRating`, `characterRating`, `enjoymentRating`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE peopleFoundUseful = VALUES(peopleFoundUseful)"

        for review in reviews:
            args = (review['workId'], review['workName'], review['postTime'], review['episodesSeen'], review['author'], review['peopleFoundUseful'], review['reviewId'],
                    review['review'], review['overallRating'], review['storyRating'], review['animationRating'], review['soundRating'], review['characterRating'], review['enjoymentRating'])
            try:
                self.__db.executeQuery(query, args)
            except Exception as e:
                print(review)
                print(e)
                break

        self.__db.databaseCommit()

    def push_work_infos_to_database(self, workInfos: list):
        query = f"INSERT INTO `{self.__workInfosTableName}` (`id`, `workId`, `workName`, `engName`, `synonymsName`, `jpName`, `workType`, `episodes`, `status`, `aired`, `premiered`, `broadcast`, `producer`, `licensors`, `studios`, `source`, `genres`, `duration`, `rating`, `score`, `scoredByUser`, `allRank`, `popularityRank`, `members`,` favorites`, `lastUpdate`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE engName = VALUES(engName), synonymsName = VALUES(synonymsName), jpName = VALUES(jpName), status = VALUES(status), aired = VALUES(aired), broadcast = VALUES(broadcast), score = VALUES(score), scoredByUser = VALUES(scoredByUser), allRank = VALUES(allRank), popularityRank = VALUES(popularityRank), members = VALUES(members), favorites = VALUES(favorites), lastUpdate = VALUES(lastUpdate)"

        logger.info('Pushing anime list data to database.')
        workInfoProgress = tqdm(workInfos, ascii=True)
        for workInfo in workInfos:
            workInfoProgress.set_description(f'Database Processing [{workInfo["workId"]}] {workInfo["workName"]}')

            args = (workInfo['workId'], workInfo['workName'], workInfo['engName'], workInfo['synonymsName'], workInfo['jpName'], workInfo['workType'], workInfo['episodes'], workInfo['status'], workInfo['aired'], workInfo['premiered'], workInfo['broadcast'], workInfo['producer'], workInfo['licensors'], workInfo['studios'], workInfo['source'], workInfo['genres'], workInfo['duration'], workInfo['rating'], workInfo['score'], workInfo['scoredByUser'], workInfo['allRank'], workInfo['popularityRank'], workInfo['members'], workInfo['favorites'], workInfo['lastUpdate'])

            try:
                self.__db.executeQuery(query, args)
            except Exception as e:
                print(workInfo)
                print(e)
                break

        self.__db.databaseCommit()

