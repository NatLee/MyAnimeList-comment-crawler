import json
import scrapy
from loguru import logger
from utils.dbUtil import AnimeAccess, Database

class ReviewSpider(scrapy.Spider):
    name = 'review_spider'
    allowed_domains = ['myanimelist.net']
    custom_settings = {
        'DOWNLOAD_DELAY': 4,
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
        self.urls = iter(self.anime_access.get_all_work_urls())  # Turn urls into an iterator

    def start_requests(self):
        url = next(self.urls)  # Get first url
        base_url = f"{url}/reviews?sort=newest&filter_check=&filter_hide=&preliminary=on&spoiler=on&p="
        yield scrapy.Request(url=base_url+'1', callback=self.parse, meta={'base_url': base_url, 'page_number': 2, 'work_url': url})

    def parse(self, response):

        reviews = []

        url = response.url
        work_id = url.split('/')[4]
        work_name = url.split('/')[5]
        logger.info(f"Processing page: [{work_id}][{work_name}]")

        review_blocks = response.css('div.review-element')

        for review in review_blocks:
            review_id = review.css('div.open a::attr(href)').re_first(r'\d+')

            # Extract the 'data-reactions' attribute and convert it to Python dictionary
            review_attrib = review.attrib
            reactions_dict = review_attrib['data-reactions']
            if reactions_dict != '':
                reactions_data = json.loads(reactions_dict)
            else:
                reactions_data = {"icon":[],"num":0,"count":["0","0","0","0","0","0","0"]}

            # Mapping the reaction types to the indexes in the icon array from data-reactions
            reaction_type_map = [
                'nice',
                'loveIt',
                'funny',
                'confusing',
                'informative',
                'wellWritten',
                'creative'
            ]
            reactions = {r:c for r,c in zip(reaction_type_map, reactions_data['count'])}
            logger.debug(f'[W{work_id}][R{review_id}] {reactions}')

            review_data = {
                'workId': work_id,
                'workName': work_name,
                'reviewId': review_id,
                'url': url,
                'postTime': review.css('div.update_at::text').get(),
                'episodesSeen': review.css('.tag.preliminary span::text').get().strip() if review.css('.tag.preliminary span::text').get() else None,
                'author': review.css('div.username a::text').get(),
                'review': ''.join(review.css('div.text *::text').getall()).strip(),
                'overallRating': review.css('div.rating span.num::text').get(),
                'reviewerProfileUrl': review.css('div.thumb a::attr(href)').get(),
                'reviewerImageUrl': review.css('div.thumb a img::attr(src)').get(),
                'recommendationStatus': review.css('.tag.recommended::text').get().strip() if review.css('.tag.recommended::text').get() else None,
            }
            review_data.update(reactions)
            reviews.append(review_data)

        # Check for "More Reviews" link existence
        next_page_exists = response.css('a.ga-click[data-ga-click-type="review-more-reviews"]::attr(href)').get()

        if not next_page_exists:
            logger.warning(f"[{work_id}][{work_name}] No next page")

            # Proceed to next work
            try:
                next_work_url = next(self.urls)
                logger.info(f'Go to next URL -> {next_work_url}')
                base_url = f'{next_work_url}/reviews?sort=newest&filter_check=&filter_hide=&preliminary=on&spoiler=on&p='
                yield scrapy.Request(url=base_url+'1', callback=self.parse, meta={'base_url': base_url, 'page_number': 2, 'work_url': next_work_url})
            except StopIteration:  # No more urls to process
                return

        logger.info(f"[{work_id}][{work_name}] Pushing {len(reviews)} reviews to the database")
        self.anime_access.push_reviews_to_database(reviews)

        base_url = response.meta['base_url']
        page_number = response.meta['page_number']
        next_page = f'{base_url}{page_number}'
        logger.info(f"[{work_id}][{work_name}] Go to next page -> Page={page_number}")
        yield scrapy.Request(next_page, self.parse, meta={'base_url': base_url, 'page_number': page_number+1, 'work_url': response.meta['work_url']})


