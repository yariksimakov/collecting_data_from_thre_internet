from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem
import scrapy


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=Python&geo%5Bt%5D%5B0%5D=4',
                  'https://spb.superjob.ru/vacancy/search/?keywords=Python']

    def __init__(self):
        super().__init__()
        self.counter = 0

    def parse(self, response: HtmlResponse):
        while self.counter < 2:
            next_page = response.xpath('//a[contains(@class, "f-test-button-dalshe")]/@href').get()
            if next_page:
                yield response.follow(next_page, callback=self.parse)
            self.counter += 1

        links = response.xpath('//div[contains(@class, "_1aHp6")]//a[@target="_blank"]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.link_parser)


    def link_parser(self, response:HtmlResponse):
        name = response.xpath('//h1/text()').get()
        salary = response.xpath('//span[contains(@class, " _2nJZK")]//text()').getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)


