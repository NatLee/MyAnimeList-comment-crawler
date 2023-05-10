
import requests
import re
import time
import os
import pickle
import multiprocessing as mp
import random
import logging
import pdb
import backoff
from tqdm import tqdm
from bs4 import BeautifulSoup  
from datetime import datetime, timedelta

from utils.miscUtil import TqdmUpTo, creationDate
from utils.gloVar import PROCESSES, HEADERS, COOKIES, TEMP_INFO_PICKLE_FOLDER, WORKINFOS_PICKLE
from utils.dbUtil import AnimeAccess, Database


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=10,
    giveup=lambda e: e.response is not None and e.response.status_code < 500
)


def allReviewCrawler(animeAccess:AnimeAccess = None, checkTime:bool = True) -> list:
    '''
    Crawl reviews on all reviews page.
    '''

    reviews = list()
    pageCounter = 1

    if animeAccess is not None:
        allWorkId = animeAccess.get_all_work_id()

    if checkTime and animeAccess is not None:
        lastReviewPostTime = animeAccess.get_last_review_post_time()
        logging.info('Last review post time: {}'.format(lastReviewPostTime['postTime'].strftime('%Y-%m-%d %H:%M:%S')))

    with TqdmUpTo(unit=' page(s) ', unit_scale=True, miniters=1, position=1) as t:
        while True:
            t.set_description('Crawling Page')
            t.updateTo(pageCounter)
            
            # block detection
            blockDetect = True
            while blockDetect:
                response = requests.get('https://myanimelist.net/reviews.php?t=anime&p=' + str(pageCounter), headers=HEADERS, cookies=COOKIES)
                webTextCount = len(response.text)
                if webTextCount < 100:
                    num = random.randint(5, 10)
                    print()
                    print('Wait {} sec(s) for unblocking'.format(str(num)))
                    time.sleep(num)
                else:
                    blockDetect = False

            soup = BeautifulSoup(response.text, 'html.parser')

            borderDarks = soup.find_all('div', attrs={ 'class' : 'borderDark' })
            pageCounter = pageCounter + 1

            if len(borderDarks) > 0:
                for borderDark in borderDarks:
                    dataFormat = { 
                        'id': None,
                        'workId': None,
                        'workName': None,
                        'postTime': None,
                        'episodesSeen': None, 
                        'author': None,
                        'peopleFoundUseful': None,
                        'reviewId': None,
                        'review': None,
                        'overallRating': None,
                        'storyRating': None,
                        'animationRating': None,
                        'soundRating': None,
                        'characterRating': None,
                        'enjoymentRating': None,
                    }

                    dataFormat['postTime'] = datetime.strptime(borderDark.find_all('div', attrs={'class': 'mb8'})[0].find_all('div')[0].get('title') + ' ' + borderDark.find_all('div', attrs={'class': 'mb8'})[0].find_all('div')[0].text, '%I:%M %p %b %d, %Y')
                    
                    dataFormat['workId'] = int(borderDark.find_all('div', 'spaceit')[0].find_all('a', 'hoverinfo_trigger')[0]['href'].split('anime/')[-1].split('/')[0])
                    dataFormat['workName'] = borderDark.find_all('div', 'spaceit')[0].find_all('a', 'hoverinfo_trigger')[0]['href'].split('anime/')[-1].split('/')[1]

                    if animeAccess is not None:
                        if dataFormat['workId'] is not None and dataFormat['workId'] not in allWorkId:
                            infoUrl = 'https://myanimelist.net/anime/{}/{}'.format(dataFormat['workId'], dataFormat['workName'])
                            logging.info('Found unknown work information. Now crawling...')
                            infoData = [infoCrawler(infoUrl)]
                            animeAccess.push_work_infos_to_database(infoData)
                            allWorkId.append(dataFormat['workId'])
                        if checkTime and (lastReviewPostTime['postTime'] > dataFormat['postTime']):
                            return reviews
                            
                    if borderDark.find_all('div', attrs={'class': 'mb8'})[0].find_all('div')[1].text.split('of')[0].replace(' ', '').replace('\n', '').find('Unknown') >= 0:
                        dataFormat['episodesSeen'] = None
                    else:
                        dataFormat['episodesSeen'] = borderDark.find_all('div', attrs={'class': 'mb8'})[0].find_all('div')[1].text.split('of')[0].replace(' ', '').replace('\n', '')
                    
                    dataFormat['author'] = borderDarks[0].find_all('a')[5].text
                    dataFormat['peopleFoundUseful'] = borderDark.find_all('div', 'lightLink spaceit')[1].find('span').text
                    dataFormat['reviewId'] = borderDark.find_all('div', 'mt12 pt4 pb4 pl0 pr0 clearfix')[0].find_all('a', 'lightLink')[0]['href'].split('id=')[-1].split('/')[0].split('?')[0]
                    context = borderDark.find_all('div', 'spaceit textReadability word-break pt8 mt8')[0].text.replace('Helpful\n\n\nread more', '')
                    
                    dataFormat['review'] = re.split(r'(\n)*.*Enjoyment\n([0-9]*)(\n)*(\s)*', context)[-1].replace('\n', '').replace('\r', '')
                    dataFormat['overallRating'] = re.findall(r'Overall\n([0-9]*)', context)[0]
                    dataFormat['storyRating'] = re.findall(r'Story\n([0-9]*)', context)[0]
                    dataFormat['animationRating'] = re.findall(r'Animation\n([0-9]*)', context)[0]
                    dataFormat['soundRating'] = re.findall(r'Sound\n([0-9]*)', context)[0]
                    dataFormat['characterRating'] = re.findall(r'Character\n([0-9]*)', context)[0]
                    dataFormat['enjoymentRating'] = re.findall(r'Enjoyment\n([0-9]*)', context)[0]

                    reviews.append(dataFormat)
            else:
                break
        
    return reviews

def reviewCrawler(workId:int = 37349, workName:str = 'Goblin_Slayer', animeAccess:AnimeAccess = None, checkTime:bool = True) -> list:
    '''
    Crawl reviews with work id and name.
    '''

    reviews = list()
    pageCounter = 1

    # cool down
    time.sleep(3)

    if checkTime and animeAccess is not None:
        allWorkLastReviewPostTimeDict = animeAccess.get_all_work_last_review_post_time()

    with TqdmUpTo(unit=' page(s) ', unit_scale=True, miniters=1, position=1) as t:
        while True:
            t.set_description('[{}] Crawling '.format(str(workId)))
            t.updateTo(pageCounter)
            
            # block detection
            blockDetect = True
            while blockDetect:
                response = requests.get('https://myanimelist.net/anime/'+ str(workId) +'/' + workName + '/reviews?p=' + str(pageCounter), headers=HEADERS, cookies=COOKIES)
                webTextCount = len(response.text)
                if webTextCount < 100:
                    num = random.randint(5, 10)
                    print()
                    logging.warning('Wait {} sec(s) for unblocking'.format(str(num)))
                    time.sleep(num)
                else:
                    blockDetect = False

            
            soup = BeautifulSoup(response.text, 'html.parser')

            borderDarks = soup.find_all('div', attrs={ 'class' : 'borderDark' })
            pageCounter = pageCounter + 1

            if len(borderDarks) > 0:
                for borderDark in borderDarks:
                    dataFormat = { 
                        'id': None,
                        'workId': workId,
                        'workName': workName,
                        'postTime': None,
                        'episodesSeen': None, 
                        'author': None,
                        'peopleFoundUseful': None,
                        'reviewId': None,
                        'review': None,
                        'overallRating': None,
                        'storyRating': None,
                        'animationRating': None,
                        'soundRating': None,
                        'characterRating': None,
                        'enjoymentRating': None,
                    }

                    dataFormat['postTime'] = datetime.strptime(borderDark.find_all('div', attrs={'class': 'mb8'})[0].find_all('div')[0].get('title') + ' ' + borderDark.find_all('div', attrs={'class': 'mb8'})[0].find_all('div')[0].text, '%I:%M %p %b %d, %Y')

                    if checkTime and animeAccess is not None:
                        workLastReviewPostTime = allWorkLastReviewPostTimeDict.get(str(workId))
                        if workLastReviewPostTime is not None and workLastReviewPostTime == dataFormat['postTime']:
                            return reviews

                    
                    if borderDark.find_all('div', attrs={'class': 'mb8'})[0].find_all('div')[1].text.split('of')[0].replace(' ', '').replace('\n', '').find('Unknown') >= 0:
                        dataFormat['episodesSeen'] = None
                    else:
                        dataFormat['episodesSeen'] = borderDark.find_all('div', attrs={'class': 'mb8'})[0].find_all('div')[1].text.split('of')[0].replace(' ', '').replace('\n', '')
                    
                    dataFormat['author'] = borderDark.find_all('a')[1]['href'].split('profile/')[-1].split('/')[0].split('?')[0]
                    dataFormat['peopleFoundUseful'] = borderDark.find_all('div', 'lightLink spaceit')[1].find('span').text
                    dataFormat['reviewId'] = borderDark.find_all('div', 'mt12 pt4 pb4 pl0 pr0 clearfix')[0].find_all('a', 'lightLink')[0]['href'].split('id=')[-1].split('/')[0].split('?')[0]
                    context = borderDark.find_all('div', 'spaceit textReadability word-break pt8 mt8')[0].text.replace('Helpful\n\n\nread more', '')
                    
                    dataFormat['review'] = re.split(r'(\n)*.*Enjoyment\n([0-9]*)(\n)*(\s)*', context)[-1].replace('\n', '').replace('\r', '')
                    dataFormat['overallRating'] = re.findall(r'Overall\n([0-9]*)', context)[0]
                    dataFormat['storyRating'] = re.findall(r'Story\n([0-9]*)', context)[0]
                    dataFormat['animationRating'] = re.findall(r'Animation\n([0-9]*)', context)[0]
                    dataFormat['soundRating'] = re.findall(r'Sound\n([0-9]*)', context)[0]
                    dataFormat['characterRating'] = re.findall(r'Character\n([0-9]*)', context)[0]
                    dataFormat['enjoymentRating'] = re.findall(r'Enjoyment\n([0-9]*)', context)[0]

                    reviews.append(dataFormat)
            else:
                break
        
    return reviews

def infoCrawler(infoUrl:str = 'https://myanimelist.net/anime/5114/Fullmetal_Alchemist__Brotherhood') -> dict:
    '''
    Crawl anime infomation.
    '''

    dataFormat = {
        'id': None,
        'workId': infoUrl.split('/')[-2],
        'workName': infoUrl.split('/')[-1],
        'engName': None,
        'synonymsName': None,
        'jpName': None,
        'workType': None,
        'episodes': None,
        'status': None,
        'aired': None,
        'permiered': None,
        'broadcast': None,
        'producer': None,
        'licensors': None,
        'studios': None,
        'source': None,
        'genres': None,
        'duration': None,
        'rating': None,
        'score': None,
        'scoredByUser': None,
        'allRank': None,
        'popularityRank': None,
        'members': None,
        'favorities': None,
        'lastUpdate': None,
    }

    if not os.path.isdir(TEMP_INFO_PICKLE_FOLDER):
        os.makedirs(TEMP_INFO_PICKLE_FOLDER)

    workIdPickle = os.path.join(TEMP_INFO_PICKLE_FOLDER, dataFormat['workId'] + '.pkl')

    if os.path.exists(workIdPickle):
        # check last update time in local pickle
        with open(workIdPickle, 'rb') as p:
            loadData = pickle.load(p)
            if (loadData['lastUpdate'] - datetime.now()) < timedelta(days=2):
                return loadData

    time.sleep(random.randint(1,5))

    slide = list()

    while len(slide) == 0:
        try:
            workResponse = requests.get(infoUrl, headers=HEADERS)
            workSoup = BeautifulSoup(workResponse.text, 'html.parser')
            slide = workSoup.find_all('div', 'js-scrollfix-bottom')
            slideText = slide[0].text
        except Exception as e:
            print(infoUrl)
            print(slide)
            time.sleep(random.randint(10,30))


    def catchSplitError(text: str, splitStrLeft: str, splitStrRight: str) -> str:
        try:
            target = text.split(splitStrLeft)[1].split(splitStrRight)[0].strip()
            if (target.find('Unknown') >= 0) or (target.find('None found, add some') >= 0):
                return None
            else:
                return target
        except Exception as e:
            #print('No this attr.>> %s' % e)
            return None
    
    dataFormat['engName'] = catchSplitError(slideText , '\nAlternative Titles\nEnglish: ', '\n')
    dataFormat['synonymsName'] = catchSplitError(slideText , '\nSynonyms: ', '\n')
    dataFormat['jpName'] = catchSplitError(slideText , '\nJapanese: ', '\n')
    dataFormat['workType'] = catchSplitError(slideText , '\nInformation\n\nType:\n', '\n')
    dataFormat['episodes'] = catchSplitError(slideText , '\nEpisodes:\n  ', '\n')
    dataFormat['status'] = catchSplitError(slideText , '\nStatus:\n  ', '\n')
    dataFormat['aired'] = catchSplitError(slideText , '\nAired:\n  ', '\n')
    dataFormat['permiered'] = catchSplitError(slideText , '\nPremiered:\n', '\n')
    dataFormat['broadcast'] = catchSplitError(slideText , '\nBroadcast:\n    ', '\n')
    if catchSplitError(slideText , '\nProducers:\n', '\n') is None:
        dataFormat['producer'] = None
    else:
        dataFormat['producer'] = catchSplitError(slideText , '\nProducers:\n', '\n').replace('       ', '')
    if catchSplitError(slideText , '\nLicensors:\n', '\n') is None:
        dataFormat['licensors'] = None
    else:
        dataFormat['licensors'] = catchSplitError(slideText , '\nLicensors:\n', '\n').replace('       ', '')
    dataFormat['studios'] = catchSplitError(slideText , '\nStudios:\n', '\n')
    dataFormat['source'] = catchSplitError(slideText , '\nSource:\n  ', '\n')
    dataFormat['genres'] = catchSplitError(slideText , '\nGenres:\n', '\n')
    dataFormat['duration'] = catchSplitError(slideText , '\nDuration:\n  ', '\n')
    dataFormat['rating'] = catchSplitError(slideText , '\nRating:\n  ', '\n')
    if slideText.find('\nStatistics\n\nScore:\nN/A') >= 0:
        dataFormat['score'] = None
    else:
        dataFormat['score'] = catchSplitError(slideText , '\nStatistics\n\nScore:\n', ' (scored by ')[:-1]

    dataFormat['scoredByUser'] = catchSplitError(slideText , ' (scored by ', ' users)\n').replace(',', '')
    if slideText.find('\nRanked:\n  N/A') >= 0:
        dataFormat['allRank'] = None
    else:
        dataFormat['allRank'] = catchSplitError(slideText , '\nRanked:\n  #', '\n')[:-1]

    dataFormat['popularityRank'] = catchSplitError(slideText , '\nPopularity:\n  #', '\n')
    dataFormat['members'] = catchSplitError(slideText , '\nMembers:\n    ', '\n').replace(',', '')
    dataFormat['favorities'] = catchSplitError(slideText , '\nFavorites:\n  ', '\n').replace(',', '')
    dataFormat['lastUpdate'] = datetime.now()

    with open(workIdPickle, 'wb') as p:
        pickle.dump(dataFormat, p)

    return dataFormat

def listCrawler() -> list:
    '''
    Crawl anime rank list.
    '''

    startRank = 0
    workInfos = list()

    with TqdmUpTo(unit=' work(s) ', unit_scale=True, miniters=1, position=1) as t:
        while True:
            t.set_description('Crawling Rank ')
            t.updateTo(startRank)

            # block detection
            blockDetect = True
            while blockDetect:
                rankResponse = requests.get('https://myanimelist.net/topanime.php?limit=' + str(startRank), headers=HEADERS)
                webTextCount = len(rankResponse.text)
                if webTextCount < 100:
                    # Random sleep 5 to 10 seconds
                    num = random.randint(5, 10)
                    #print('[WARNING] Wait %s sec(s) for unblocking' % str(num))
                    time.sleep(num)
                else:
                    blockDetect = False


            rankSoup = BeautifulSoup(rankResponse.text, 'html.parser')

            works = rankSoup.find_all('tr', attrs = {'class':'ranking-list'})
            startRank = startRank + 50
        
            if len(works) != 0:
                
                infoUrls = list()

                for work in works:
                    infoUrls.append(work.find('a', attrs= {'class': 'hoverinfo_trigger fl-l ml12 mr8'})['href'])

                with mp.Pool(processes=PROCESSES) as p:
                    result = p.map(infoCrawler,infoUrls)

                workInfos = workInfos + result
            else:
                break

    return workInfos

class Crawler(object):
    def __init__(self, database: Database = None, checkTime:bool = True):
        self.__database = database
        self.__animeAccess = AnimeAccess(self.__database)
        self.__checkTime = checkTime
        self.__workInfos = None
        self.__reviews = None
        
    def getWorkInfos(self) -> list:
        '''
        Crawl all work infomation.
        '''
        workInfos = self.__checkWorkInfos(days=7)
        if workInfos is None:
            self.__workInfos = listCrawler()
            with open(WORKINFOS_PICKLE, 'wb') as p:
                pickle.dump(self.__workInfos, p)
        return self.__workInfos

    def __checkWorkInfos(self, days:int = 3) -> list:
        '''
        Check the workInfos.pkl file exist.
        '''
        # Read workInfos.pkl if exists or crawl work infos.
        if os.path.isfile(WORKINFOS_PICKLE) and (datetime.today() - creationDate(WORKINFOS_PICKLE) < timedelta(days=days)):
            logging.info('Detect %s file.' % WORKINFOS_PICKLE)
            with open(WORKINFOS_PICKLE, 'rb') as p:
                self.__workInfos = pickle.load(p)
        return self.__workInfos

    def setReviews(self, reviews:list) -> list:
        '''
        Set reviews attribute.
        '''
        self.__reviews = reviews
        return self.__reviews

    def getAllReviews(self) -> list:
        '''
        Crawl reviews in all review page.
        '''
        reviews = allReviewCrawler(animeAccess=self.__animeAccess, checkTime=self.__checkTime)
        return self.setReviews(reviews)

    def getReviewsByWork(self, workId:int, workName:str):
        '''
        Crawl reviews by work.
        '''
        reviews = reviewCrawler(workId=workId, workName=workName, animeAccess=self.__animeAccess)
        return self.setReviews(reviews)

    def pushReviewsToDatabase(self):
        '''
        Push reviews to database.
        '''
        if self.__reviews is not None:
            self.__animeAccess.push_reviews_to_database(reviews=self.__reviews)
        return

    def pushReviewsToDatabaseByWorkInfos(self):
        '''
        After crawl all work information, then crawl and push their reviews to database.
        '''
        if self.__workInfos is not None:
            logging.info('Starting crawl reviews with work infos.')
            workInfoProgress = tqdm(self.__workInfos)
            for workInfo in workInfoProgress:
                workInfoProgress.set_description('Review Processing [%s] %s' % (workInfo['workId'], workInfo['workName']))
                _ = self.getReviewsByWork(workId=workInfo['workId'], workName=workInfo['workName'])
                # push one work reviews to db
                self.pushReviewsToDatabase()
        return

    def pushWorkInfosToDatabase(self):
        '''
        Push work information to database.
        '''
        if self.__workInfos is not None:
            self.__animeAccess.push_work_infos_to_database(workInfos=self.__workInfos)
        return

    def updateDataByAllReviewsPage(self):
        _ = self.getAllReviews()
        self.pushReviewsToDatabase()
        return

    def updateDataByOneWork(self, workId:int, workName:str):
        self.getReviewsByWork(workId=workId, workName=workName)
        self.pushReviewsToDatabase()
        return

    def updateDataWorkByWork(self):
        _ = self.getWorkInfos()
        self.pushWorkInfosToDatabase()
        self.pushReviewsToDatabaseByWorkInfos()
        return
