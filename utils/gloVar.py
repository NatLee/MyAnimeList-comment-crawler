import configparser
import os

HEADERS = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

COOKIES = {'reviews_inc_preliminary': '1', 'reviews_sort': 'recent'}


CONFIG = configparser.ConfigParser()
CONFIG.read('setting.ini')

DEBUG = CONFIG.getboolean('MODE', 'Debug')
PROCESSES = CONFIG.getint('SETTING', 'ProcessesNumber')

WORK_DIR = os.getcwd()
TEMP_INFO_FOLDER = os.path.join(WORK_DIR, CONFIG.get('PATH', 'TempWorkInfoFolder'))
WORK_INFOS = os.path.join(WORK_DIR, CONFIG.get('PATH', 'WorkInfosPath'))

DATABASE_NAME = CONFIG.get('DATABASE', 'DatabaseName')

