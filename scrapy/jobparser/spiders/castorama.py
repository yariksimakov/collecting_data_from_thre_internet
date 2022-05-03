from scrapy.http import HtmlResponse
import scrapy
from scrapy.loader import ItemLoader

from jobparser.items import JobparserItem


class CastoramaSpider(scrapy.Spider):
    name = 'castorama'
    allowed_domains = ['castorama.ru']
    # start_urls = ['https://www.castorama.ru/bathroom/shower-stalls']

    def __init__(self, name=None, **kwargs):
        super(CastoramaSpider, self).__init__(name, **kwargs)
        self.start_urls = [f'https://www.castorama.ru/bathroom/{kwargs["product"]}']


    def parse(self, response: HtmlResponse):
        links = response.xpath('//a[contains(@class, "product-card__img")]/@href')
        for link in links:
            yield response.follow(link, callback=self.parser_data)

    def parser_data(self, response: HtmlResponse):
        loader = ItemLoader(item=JobparserItem(), response=response)
        loader.add_xpath('product_name', '//h1/text()')
        loader.add_xpath('price', '//span[contains(@id, "product-price")]/span/span/span[1]') # start
        loader.add_xpath('photos', '//ul[@class="swiper-wrapper"]//span/@content')
        loader.add_value('url', response.url)
        yield loader.load_item()


