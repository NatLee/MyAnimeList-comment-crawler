import datetime
import re

import requests
from bs4 import BeautifulSoup

from loguru import logger

class AnimeDataExtractor:
    def __init__(self, url):
        self.url = url
        logger.info(f'URL -> {self.url}')
        self.work_id = int(self.url.split('/')[-2])
        self.work_name =  self.url.split('/')[-1]
        self.html = None
        self.soup = None

    def get_html(self):
        text = requests.get(self.url).text
        self.html = text
        self.soup = BeautifulSoup(text, 'html.parser')
        return text

    def extract_score(self):
        score_div = self.soup.find('div', class_='score')
        score_label = score_div.find('div', class_='score-label').text.strip()
        return float(score_label)

    def extract_rank(self):
        rank_span = self.soup.find('span', class_='numbers ranked')
        rank = re.search(r'#(\d+)', rank_span.text)
        if rank:
            return int(rank.group(1))
        return None

    def extract_popularity_rank(self):
        popularity_span = self.soup.find('span', class_='numbers popularity')
        popularity_rank = re.search(r'#(\d+)', popularity_span.text)
        if popularity_rank:
            return int(popularity_rank.group(1))
        return None

    def extract_members(self):
        members_span = self.soup.find('span', class_='numbers members')
        members = re.sub(r'[^\d]', '', members_span.text)
        if members:
            return int(members)
        return None

    def extract_synonyms(self):
        logger.info(f'synonyms ::: {self.url}')
        try:
            text = self.soup.find('h2', string='Alternative Titles').find_next('span', class_='dark_text', string='Synonyms:').parent.text
        except AttributeError:
            logger.warning(f'synonyms ::: PARENT NOT FOUND ::: {self.url}')
            return None
        text = text.replace('\n', '').replace('Synonyms:', '').strip()
        if text:
            return text
        return None

    def extract_japanese_name(self):
        logger.info(f'japanese name  ::: {self.url}')
        try:
            text = self.soup.find('h2', string='Alternative Titles').find_next('span', class_='dark_text', string='Japanese:').parent.text
        except AttributeError:
            logger.warning(f'japanese name ::: PARENT NOT FOUND ::: {self.url}')
            return None
        text = text.replace('\n', '').replace('Japanese:', '').strip()
        if text:
            return text
        return None

    def extract_english_name(self):
        logger.info(f'english name  ::: {self.url}')
        try:
            text = self.soup.find('h2', string='Alternative Titles').find_next('span', class_='dark_text', string='English:').parent.text
        except AttributeError:
            logger.warning(f'english name ::: PARENT NOT FOUND ::: {self.url}')
            return None
        text = text.replace('\n', '').replace('English:', '').strip()
        if text:
            return text
        return None

    def extract_type(self):
        type_div = self.soup.find('span', class_='dark_text', string='Type:').find_next('a')
        if type_div:
            return type_div.text.strip()
        return None

    def extract_episodes(self):
        episodes_div = self.soup.find('span', class_='dark_text', string='Episodes:').find_parent()
        episodes = re.search(r'Episodes:\n\s+(.*)\n', episodes_div.text)
        if episodes:
            return episodes.group(1).strip()
        return None

    def extract_status(self):
        status_div = self.soup.find('span', class_='dark_text', string='Status:').find_parent()
        status = re.search(r'Status:\n\s+(.*)\n', status_div.text)
        if status:
            return status.group(1).strip()
        return None

    def extract_aired(self):
        aired_div = self.soup.find('span', class_='dark_text', string='Aired:').find_parent()
        aired = re.search(r'Aired:\n\s+(.*)\n', aired_div.text)
        if aired:
            return aired.group(1).strip()
        return None

    def extract_premiered(self):
        logger.info(f'premiered ::: {self.url}')
        try:
            premiered_div = self.soup.find('span', class_='dark_text', string='Premiered:').find_parent()
        except AttributeError:
            logger.warning(f'premiered ::: PARENT NOT FOUND ::: {self.url}')
            return None
        premiered = premiered_div.text.replace('Premiered:', '').replace('\n', '').strip()
        if premiered:
            return premiered
        return None

    def extract_broadcast(self):
        try:
            broadcast_div = self.soup.find('span', class_='dark_text', string='Broadcast:').find_parent()
        except AttributeError:
            logger.warning(f'broadcast ::: PARENT NOT FOUND ::: {self.url}')
            return None
        broadcast = re.search(r'Broadcast:\n\s+(.*)\n', broadcast_div.text)
        if broadcast:
            return broadcast.group(1).strip()
        return None

    def extract_producers(self):
        producers_div = self.soup.find('span', class_='dark_text', string='Producers:').parent
        if producers_div:
            producers = producers_div.find_all('a', href=True)
            return [producer.text.strip() for producer in producers]
        return None

    def extract_licensors(self):
        licensors_div = self.soup.find('span', class_='dark_text', string='Licensors:').parent
        if licensors_div:
            licensors = licensors_div.find_all('a', href=True)
            return [licensor.text.strip() for licensor in licensors]
        return None

    def extract_studios(self):
        studios_div = self.soup.find('span', class_='dark_text', string='Studios:').find_parent()
        studios = re.search(r'Studios:\n(.*)', studios_div.text)
        if studios:
            return studios.group(1).strip()
        return None

    def extract_genres(self):
        logger.info(f'genres ::: {self.url}')
        genres_list = []
        try:
            genres_divs = self.soup.find('span', class_='dark_text', string='Genre:')
        except AttributeError:
            logger.warning(f' genres ::: GENRE NOT FOUND ::: {self.url}')
        if not genres_divs:
            try:
                genres_divs = self.soup.find('span', class_='dark_text', string='Genres:')
            except AttributeError:
                logger.warning(f' genres ::: GENRE"S" NOT FOUND ::: {self.url}')
                return genres_list
        if genres_divs:
            genres_divs = genres_divs.parent.find_all('span', itemprop='genre')
        else:
            return genres_list
        if genres_divs:
            for genre_div in genres_divs:
                genres_text = genre_div.text.strip()
            genres_list = [genre.strip() for genre in genres_text.split(',')]
            return genres_list
        return genres_list

    def extract_duration(self):
        duration_div = self.soup.find('span', class_='dark_text', string='Duration:').find_parent()
        duration = re.search(r'Duration:\n\s+(.*)\n', duration_div.text)
        if duration:
            return duration.group(1).strip()
        return None

    def extract_scored_by_users(self):
        rating_count_span = self.soup.find('span', itemprop='ratingCount')
        if rating_count_span:
            return int(rating_count_span.text.replace(',', ''))
        return None

    def extract_favorites(self):
        favorites_div = self.soup.find('span', class_='dark_text', string='Favorites:').find_parent()
        favorites = re.search(r'Favorites:\n\s+(.*)\n', favorites_div.text)
        if favorites:
            return int(favorites.group(1).strip().replace(',', ''))
        return None

    def extract_rating(self):
        rating_div = self.soup.find('span', class_='dark_text', string='Rating:').find_parent()
        rating = re.search(r'Rating:\n\s+(.*)\n', rating_div.text)
        if rating:
            return rating.group(1).strip()
        return None

    def extract_source(self):
        source_div = self.soup.find('span', class_='dark_text', string='Source:').find_parent()
        source = re.search(r'Source:\n\s+(.*)\n', source_div.text)
        if source:
            return source.group(1).strip()
        return None


    def format_data(self):
        if not self.soup or not self.html:
            raise ValueError("Need to run `get_html` at first!")
        dataFormat = {
            'id': None,
            'workId': self.work_id,
            'workName': self.work_name,
            'engName': self.extract_english_name(),
            'synonymsName': self.extract_synonyms(),
            'jpName': self.extract_japanese_name(),
            'workType': self.extract_type(),
            'episodes': self.extract_episodes(),
            'status': self.extract_status(),
            'aired': self.extract_aired(),
            'premiered': self.extract_premiered(),
            'broadcast': self.extract_broadcast(),
            'producer': self.extract_producers(),
            'licensors': self.extract_licensors(),
            'studios': self.extract_studios(),
            'source': self.extract_source(),
            'genres': self.extract_genres(),
            'duration': self.extract_duration(),
            'rating': self.extract_rating(),
            'score': self.extract_score(),
            'scoredByUser': self.extract_scored_by_users(),
            'allRank': self.extract_rank(),
            'popularityRank': self.extract_popularity_rank(),
            'members': self.extract_members(),
            'favorites': self.extract_favorites(),
            'lastUpdate': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        return dataFormat



import requests
url = 'https://myanimelist.net/anime/40664/Shoujo☆Kageki_Revue_Starlight_Movie'

ade = AnimeDataExtractor(url=url)
ade.get_html()
from pprint import pprint
pprint(ade.format_data())


