from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from jobparser.spiders.hhru import HhruSpider
<<<<<<< HEAD
from jobparser.spiders.sjru import SjruSpider
=======
>>>>>>> origin/sixth_lesson

if __name__ == '__main__':
    configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
<<<<<<< HEAD
    # runner.crawl(HhruSpider)
    runner.crawl(SjruSpider)
=======
    runner.crawl(HhruSpider)
    # runner.crawl(SjruSpider)
>>>>>>> origin/sixth_lesson
    #
    # d = runner.join()
    # d.addBoth(lambda _: reactor.stop())

    reactor.run()
