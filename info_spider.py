from pathlib import Path
import json
import datetime

import scrapy
from loguru import logger

from utils.dbUtil import AnimeAccess, Database
from utils.gloVar import TEMP_INFO_FOLDER, RANK_INCREMENT

class InfoSpider(scrapy.Spider):
    name = 'info_spider'
    custom_settings = {
        'DOWNLOAD_DELAY': 7,
        #'RETRY_HTTP_CODES': [429],
        #'RETRY_TIMES': 10
    }
    DOWNLOADER_MIDDLEWARES = {
        'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
    }
    # Disable cookies (enabled by default)
    COOKIES_ENABLED = False

    def __init__(self):
        self.db = Database()
        self.anime_access = AnimeAccess(self.db)

    def start_requests(self):
        rank_url = 'https://myanimelist.net/topanime.php?limit=0'
        yield scrapy.Request(url=rank_url, callback=self.parse_rank)

    def parse_rank(self, response):
        works = response.css('tr.ranking-list')
        info_urls = [work.css('a.hoverinfo_trigger.fl-l.ml12.mr8::attr(href)').get() for work in works]
        
        for info_url in info_urls:
            work_id = info_url.split('/')[4]
            work_id_name = str(work_id).zfill(6)
            work_id_file = Path(TEMP_INFO_FOLDER) / f'{work_id_name}.json'

            if not work_id_file.exists():  # check if JSON file exists
                yield scrapy.Request(url=info_url, callback=self.parse_info)
            else:
                logger.debug(f'[{work_id_name}] - JSON file exists')
        
        # Extract current limit from the URL
        current_limit = int(response.url.split('=')[-1])
        
        # If there are more pages, generate a request to the next page
        if works:
            next_limit = current_limit + RANK_INCREMENT
            next_url = f'https://myanimelist.net/topanime.php?limit={next_limit}'
            yield scrapy.Request(url=next_url, callback=self.parse_rank)

    def parse_info(self, response):
        url = response.url
        work_id = response.url.split('/')[4]
        data = {
            'workId': work_id,
            'url': url,
            'jpName': response.xpath('//span[contains(text(), "Japanese:")]/following::text()').get(default='').strip(),
            'engName': response.xpath('//span[contains(text(), "English:")]/following::text()').get(default='').strip(),
            'synonymsName': response.xpath('//span[contains(text(), "Synonyms:")]/following::text()').get(default='').strip(),
            'workType': response.xpath('//span[text()="Type:"]/following-sibling::a/text()').get(default=''),
            'episodes': response.xpath('//span[text()="Episodes:"]/following::text()').get(default='').strip(),
            'status': response.xpath('//span[text()="Status:"]/following::text()').get(default='').strip(),
            'aired': response.xpath('//span[text()="Aired:"]/following::text()').get(default='').strip(),
            'premiered': response.xpath('//span[text()="Premiered:"]/following-sibling::a/text()').get(default=''),
            'producer': ', '.join(response.xpath('//span[text()="Producers:"]/following-sibling::a/text()').getall()),
            'broadcast': response.xpath('//span[contains(text(), "Broadcast:")]/following-sibling::text()').get(default='').strip(),
            'licensors': response.xpath('//span[text()="Licensors:"]/following-sibling::a/text()').get(default=''),
            'studios': response.xpath('//span[text()="Studios:"]/following-sibling::a/text()').get(default=''),
            'genres': response.xpath('//span[text()="Genres:"]/following-sibling::a/text()').get(default=''),
            'source': response.xpath('//span[contains(text(), "Source:")]/following-sibling::text()').get(default='').strip(),
            'duration': response.xpath('//span[contains(text(), "Duration:")]/following-sibling::text()').get(default='').strip(),
            'rating': response.xpath('//span[text()="Rating:"]/following::text()').get().strip(),
            'score': response.css('span.score-label::text').get(default=''),
            'allRank': response.xpath('//span[text()="Ranked:"]/following::text()').get(default='').strip(),
            'popularityRank': response.xpath('//span[text()="Popularity:"]/following::text()').get(default='').strip(),
            'members': response.xpath('//span[text()="Members:"]/following::text()').get(default='').strip(),
            'favorites': response.xpath('//span[text()="Favorites:"]/following::text()').get(default='').strip(),
            'scoredByUser': response.xpath('//span[@itemprop="ratingCount"]/text()').get(default='').strip(),
            'lastUpdate': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        temp = Path(TEMP_INFO_FOLDER)
        if not temp.is_dir():
            temp.mkdir(parents=True, exist_ok=True)

        work_id_name = str(work_id).zfill(6)
        work_id_file = temp / f'{work_id_name}.json'

        with open(work_id_file, 'w', encoding='utf-8') as p:
            json.dump(data, p, indent=4, ensure_ascii=False)

        self.anime_access.push_work_infos_to_database([data])

        yield data