import pymysql
import logging
from tqdm import tqdm
from utils.gloVar import DATABASE_NAME, CHAR_SET, HOST, PORT, USER, PWD

class Database(object):
    __single = None
    def __new__(clz):
        if not Database.__single:
            Database.__username = USER
            Database.__password = PWD
            Database.__host = HOST
            Database.__port = PORT
            Database.__db = DATABASE_NAME
            Database.__charset = CHAR_SET
            Database.__cursor = pymysql.cursors.DictCursor
            conn = pymysql.connect(host=Database.__host,\
                                user=Database.__username,\
                                password=Database.__password,\
                                db=Database.__db,\
                                port=Database.__port,\
                                charset=Database.__charset,\
                                cursorclass=Database.__cursor)
            Database.__conn = conn
            Database.__single = object.__new__(clz)
        return Database.__single

    def __getConnection(self):
        self.checkConnection()
        return self.__conn

    def getConnection(self):
        return self.__getConnection()
        
    def checkConnection(self):
        return self.__conn.ping(reconnect=True)

    def executeQuery(self, query: str, args: tuple):
        self.checkConnection()
        result = dict()
        with self.__conn.cursor() as cursor:
            cursor.execute(query, args)
            result = cursor.fetchall()
        return result

    def databaseCommit(self):
        return self.__conn.commit()

class AnimeAccess(object):
    
    def __init__(self, db:Database):
        self.__db = db
        self.__allReviewsLastPostTime = None
        self.__lastReviewPostTime = None

        self.__reviewsTableName = 'reviews'
        self.__workInfosTableName = 'animeList'

    def getAllWorkIdAndReview(self) -> dict:

        '''
        520  words  cover 68%
        1000 words  cover 90% 
        1200 words  cover 95%
        1880 words  cover 99.7%
        '''

        result = self.__db.executeQuery('select reviewId, review from reviews', None)

        data = {
            'ids'    :list(),
            'reviews':list(),
            'lengths':list()
        }

        for element in result:
            data['ids'].append(element['reviewId'])
            data['reviews'].append(element['review'])
            data['lengths'].append(len(element['review'].split(' ')))

        return data

    def getAllWorkLastReviewPostTime(self) -> dict:
        
        if self.__allReviewsLastPostTime is None:

            results = self.__db.executeQuery('select workId, max(postTime) as postTime from reviews group by workId', None)

            self.__allReviewsLastPostTime = dict()

            for result in results:
                self.__allReviewsLastPostTime[str(result['workId'])] = result['postTime']

        return self.__allReviewsLastPostTime

    def getAllWorkId(self) -> list:

        query = 'select workId from ' + self.__workInfosTableName
        results = self.__db.executeQuery(query, None)

        allWorkId = list()

        for result in results:
            allWorkId.append(result.get('workId'))

        return allWorkId


    def getLastReviewPostTime(self) -> dict:

        if self.__lastReviewPostTime is None:
            results = self.__db.executeQuery('select workId, postTime from reviews order by postTime desc limit 1', None)

            self.__lastReviewPostTime = results[0]
        
        return self.__lastReviewPostTime

    def pushReviewsToDatabase(self, reviews: list):
        query: str = "INSERT INTO `" + self.__reviewsTableName + \
            "` (`id`, `workId`, `workName`, `postTime`, `episodesSeen`, `author`, `peopleFoundUseful`, `reviewId`, `review`, `overallRating`, `storyRating`, `animationRating`, `soundRating`, `characterRating`, `enjoymentRating`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE peopleFoundUseful = VALUES(peopleFoundUseful)"

        for review in reviews:

            args = (review['workId'], review['workName'], review['postTime'], review['episodesSeen'],  review['author'], review['peopleFoundUseful'], review['reviewId'],
                    review['review'], review['overallRating'], review['storyRating'], review['animationRating'], review['soundRating'], review['characterRating'], review['enjoymentRating'])
            try:
                self.__db.executeQuery(query, args)
            except Exception as e:
                print(review)
                print(e)
                break

        self.__db.databaseCommit()

    def pushWorkInfosToDatabase(self, workInfos: list):
        
        query: str = "INSERT INTO `" + self.__workInfosTableName + \
                "` (`id`, `workId`, `workName`, `engName`, `synonymsName`, `jpName`, `workType`, `episodes`, `status`, `aired`, `permiered`, `broadcast`, `producer`, `licensors`, `studios`, `source`, `genres`, `duration`, `rating`, `score`, `scoredByUser`, `allRank`, `popularityRank`, `members`, `favorities`, `lastUpdate`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE engName = VALUES(engName), synonymsName = VALUES(synonymsName), jpName = VALUES(jpName), status = VALUES(status), aired = VALUES(aired), broadcast = VALUES(broadcast), score = VALUES(score), scoredByUser = VALUES(scoredByUser), allRank = VALUES(allRank), popularityRank = VALUES(popularityRank), members = VALUES(members), favorities = VALUES(favorities), lastUpdate = VALUES(lastUpdate)"
        
        # push work infos to db
        
        logging.info('Pushing anime list data to database.')
        workInfoProgress = tqdm(workInfos, ascii=True)
        for workInfo in workInfos:

            workInfoProgress.set_description('Database Processing [%s] %s' % (workInfo['workId'], workInfo['workName']))

            args = (workInfo['workId'], workInfo['workName'], workInfo['engName'], workInfo['synonymsName'], workInfo['jpName'], workInfo['workType'], workInfo['episodes'], workInfo['status'], workInfo['aired'], workInfo['permiered'], workInfo['broadcast'], workInfo['producer'], workInfo['licensors'], workInfo['studios'], workInfo['source'], workInfo['genres'], workInfo['duration'], workInfo['rating'], workInfo['score'], workInfo['scoredByUser'], workInfo['allRank'], workInfo['popularityRank'], workInfo['members'], workInfo['favorities'], workInfo['lastUpdate'])

            try:
                self.__db.executeQuery(query, args)
            except Exception as e:
                print(workInfo)
                print(e)
                break

        self.__db.databaseCommit()
