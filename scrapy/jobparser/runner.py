from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from jobparser.spiders.instagram import InstagramSpider
from jobparser.spiders.castorama import CastoramaSpider
from jobparser.spiders.hhru import HhruSpider
from jobparser.spiders.sjru import SjruSpider
from jobparser.spiders.leroymerlin import LeroymerlinSpider

if __name__ == '__main__':
    configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    # runner.crawl(CastoramaSpider, product='shower-stalls')
    runner.crawl(InstagramSpider)
    # d = runner.join()
    # d.addBoth(lambda _ : reactor.stop())

    reactor.run()
