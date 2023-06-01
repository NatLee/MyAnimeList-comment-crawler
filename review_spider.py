import scrapy
from tqdm import tqdm
from loguru import logger
from utils.dbUtil import AnimeAccess, Database

class ReviewSpider(scrapy.Spider):
    name = 'review_spider'
    allowed_domains = ['myanimelist.net']
    custom_settings = {
        'DOWNLOAD_DELAY': 10,
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
        self.urls = self.anime_access.get_all_work_urls()

    def start_requests(self):
        self.urls = iter(self.anime_access.get_all_work_urls())  # Turn urls into an iterator
        url = next(self.urls)  # Get first url
        base_url = url + '/reviews?sort=newest&filter_check=&filter_hide=&preliminary=on&spoiler=on&p='
        yield scrapy.Request(url=base_url+'1', callback=self.parse, meta={'base_url': base_url, 'page_number': 2, 'work_url': url})

    def parse(self, response):
        url = response.url
        work_id = url.split('/')[4]
        work_name = url.split('/')[5]
        logger.info(f"Processing page: [{work_id}][{work_name}]")

        review_blocks = response.css('div.review-element')

        if not review_blocks:
            logger.warning(f"No review blocks found on page: {url}")

            # Proceed to next work
            try:
                next_work_url = next(self.urls)
                base_url = next_work_url + '/reviews?sort=newest&filter_check=&filter_hide=&preliminary=on&spoiler=on&p='
                yield scrapy.Request(url=base_url+'1', callback=self.parse, meta={'base_url': base_url, 'page_number': 2, 'work_url': next_work_url})
            except StopIteration:  # No more urls to process
                return
        else:
            reviews = []
    
            for review in tqdm(review_blocks):
                reactions = review.css('.btn-reaction .num::text').getall()
                review_id = review.css('div.open a::attr(href)').re_first(r'\d+')

                '''
                # Check if review already exists in the database
                if self.anime_access.review_exists(review_id):
                    continue
                '''

                review_data = {
                    'workId': work_id,
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
                    'nice': reactions[0],
                    'loveIt': reactions[1],
                    'funny': reactions[2],
                    'confusing': reactions[3] if len(reactions) > 3 else None,
                    'informative': reactions[4] if len(reactions) > 4 else None,
                    'wellWritten': reactions[5] if len(reactions) > 5 else None,
                    'creative': reactions[6] if len(reactions) > 6 else None,
                }
                reviews.append(review_data)

            logger.info(f"Pushing {len(reviews)} reviews to the database")
            self.anime_access.push_reviews_to_database(reviews)

            base_url = response.meta['base_url']
            page_number = response.meta['page_number']
            next_page = f'{base_url}{page_number}'
            logger.info(f"Following link to next page: [{work_id}][{work_name}] -> Page={page_number}")
            yield scrapy.Request(next_page, self.parse, meta={'base_url': base_url, 'page_number': page_number+1, 'work_url': response.meta['work_url']})


