import datetime
import json
from pathlib import Path
import requests
import re
import time
import os
import multiprocessing as mp
import random

from loguru import logger

import backoff
from tqdm import tqdm
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from utils.extractor import AnimeDataExtractor

from utils.miscUtil import TqdmUpTo, creationDate
from utils.gloVar import PROCESSES, HEADERS, COOKIES, TEMP_INFO_FOLDER, WORK_INFOS
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
        logger.info('Last review post time: {}'.format(lastReviewPostTime['postTime'].strftime('%Y-%m-%d %H:%M:%S')))

    with TqdmUpTo(unit=' page(s) ', unit_scale=True, miniters=1, position=1) as t:
        while True:
            t.set_description('Crawling Page')
            t.updateTo(pageCounter)
            
            # block detection
            blockDetect = True
            while blockDetect:
                response = requests.get(
                    f'https://myanimelist.net/reviews.php?t=anime&p={pageCounter}',
                    headers=HEADERS,
                    cookies=COOKIES
                )
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
                            infoUrl = f"https://myanimelist.net/anime/{dataFormat['workId']}/{dataFormat['workName']}"

                            logger.info('Found unknown work information. Now crawling...')

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
                    logger.warning('Wait {} sec(s) for unblocking'.format(str(num)))
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

def infoCrawler(infoUrl:str = 'https://myanimelist.net/anime/52034/Oshi_no_Ko') -> dict:
    '''
    Crawl Anime Information.
    '''

    ade = AnimeDataExtractor(url=infoUrl)

    temp = Path(TEMP_INFO_FOLDER)
    if not temp.is_dir():
        temp.mkdir(parents=True, exist_ok=True)

    work_id_name = str(ade.work_id).zfill(6)
    work_id_file = temp / f'{work_id_name}.json'

    if work_id_file.exists():
        logger.info(f'Find -> {work_id_file}')
        # check last update time in local file
        with open(work_id_file, 'r', encoding='utf-8') as p:
            loadData = json.loads(p.read())
            last_update = loadData.get('lastUpdate')
            last_update = datetime.strptime(last_update, '%Y-%m-%d %H:%M:%S')
            if (last_update - datetime.now()) < timedelta(days=2):
                return loadData

    time.sleep(random.randint(1,5))

    try:
        ade.get_html()
    except Exception as e:
        print(e)
        print(infoUrl)
        raise RuntimeError('You got banned!!')

    data_format = ade.format_data()

    with open(work_id_file, 'w', encoding='utf-8') as p:
        json.dump(data_format, p, indent=4, ensure_ascii=False)

    return data_format

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
                rankResponse = requests.get(f'https://myanimelist.net/topanime.php?limit={startRank}', headers=HEADERS)
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
        Crawl all work information.
        '''
        workInfos = self.__checkWorkInfos(days=7)
        if workInfos is None:
            self.__workInfos = listCrawler()
            with open(WORK_INFOS, 'w', encoding='utf-8') as p:
                json.dump(self.__workInfos, p, indent=4, ensure_ascii=False)
        return self.__workInfos

    def __checkWorkInfos(self, days:int = 3) -> list:
        '''
        Check the workInfos.pkl file exist.
        '''
        # Read workInfos.pkl if exists or crawl work infos.
        if os.path.isfile(WORK_INFOS) and (datetime.today() - creationDate(WORK_INFOS) < timedelta(days=days)):
            logger.info(f'Detect [{WORK_INFOS}] file.')
            with open(WORK_INFOS, 'r', encoding='utf-8') as p:
                self.__workInfos = json.loads(p.read())
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
            logger.info('Starting crawl reviews with work infos.')
            workInfoProgress = tqdm(self.__workInfos)
            for workInfo in workInfoProgress:
                workInfoProgress.set_description(f"Review Processing [{workInfo['workId']}] {workInfo['workName']}")
                _ = self.getReviewsByWork(
                    workId=workInfo['workId'],
                    workName=workInfo['workName']
                )
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
