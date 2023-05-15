import argparse
from utils.dbUtil import Database
from utils.crawlUtil import Crawler

parser = argparse.ArgumentParser(description='Dataset parse.')
parser.add_argument('--updateByAllReviewPage', action='store', nargs='?', const=True, default=False, type=bool, help='Update database by crawling all review page. (Fast)')
parser.add_argument('--updateDataByWork', action='store', nargs='?', const=True, default=False, type=bool, help='Update database by crawling review page for each work. (Slow)')
config = parser.parse_args()
parser.print_help()

if __name__ == '__main__':

    db = Database()

    crawler = Crawler(database=db, checkTime=True)

    if config.updateByAllReviewPage:
        # Crawl from all reviews page.
        crawler.updateDataByAllReviewsPage()

    if config.updateDataByWork:
        # Crawl work by work.
        crawler.updateDataWorkByWork()

