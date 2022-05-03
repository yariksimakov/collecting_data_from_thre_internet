# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from itemloaders.processors import MapCompose, TakeFirst
import re
import scrapy


def processing_price(value):
    price_str = re.findall(r'\d+.\d+', value)[0].replace(' ', '')
    return int(price_str)


class JobparserItem(scrapy.Item):
    # define the fields for your item here like:
    product_name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(processing_price), output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    _id = scrapy.Field()
    # salary = scrapy.Field()
    # min_salary = scrapy.Field()
    # max_salary = scrapy.Field()
    # currency = scrapy.Field()

