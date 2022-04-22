from scrapy.http import HtmlResponse
import scrapy
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://spb.hh.ru/search/vacancy?area=2&search_field=name&search_field=company_name&search_field=description&text=python',
                  'https://spb.hh.ru/search/vacancy?area=1&search_field=name&search_field=company_name&search_field=description&text=python']

<<<<<<< HEAD
    def __init__(self):
        super().__init__()
        self.counter = 0

    def parse(self, response: HtmlResponse):
        while self.counter < 2:
            next_page = response.xpath('//a[@data-qa = "pager-next"]/@href').get()
            if next_page:
                yield response.follow(next_page, callback=self.parse)
            self.counter += 1

=======
    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@data-qa = "pager-next"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
>>>>>>> origin/sixth_lesson
        links = response.xpath('//a[@data-qa = "vacancy-serp__vacancy-title"]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parser)

<<<<<<< HEAD
=======

>>>>>>> origin/sixth_lesson
    def vacancy_parser(self, response: HtmlResponse):
        name = response.css('h1::text').get()
        salary = response.xpath('//div[@data-qa="vacancy-salary"]//text()').getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)
