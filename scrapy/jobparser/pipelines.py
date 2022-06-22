# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.utils.python import to_bytes
import scrapy
import hashlib
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
import re


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_data_base = client.vacancy_database

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['min_salary'], item['max_salary'], item['currency'] = self.process_salary_for_hhru(item['salary'])
            del item['salary']
        elif spider.name == 'sjru':
            item['min_salary'], item['max_salary'], item['currency'] = self.process_salary_for_sjru(item['salary'])
            del item['salary']

        collection = self.mongo_data_base[spider.name]
        collection.insert_one(item)
        # print(spider.name)
        return item

    def process_salary_for_hhru(self, salary):
        min_salary = None
        max_salary = None
        currency = None
        if len(salary) != 1:
            if len(salary) == 5:
                currency = salary[3]
                if salary[0] == 'до':
                    max_salary = salary[1]
                else:
                    min_salary = salary[1]

            elif len(salary) == 7:
                max_salary = salary[3]
                min_salary = salary[1]
                currency = salary[5]

        return min_salary, max_salary, currency

    def process_salary_for_sjru(self, salary):
        min_salary = None
        max_salary = None
        currency = None
        if len(salary) == 5:
            currency = re.findall(r'(\w{3}).$', salary[2])[0]
            if salary[0] == 'от':
                min_salary = re.findall(r'\d+\s\d+', salary[2])[0]
            else:
                max_salary = re.findall(r'\d+\s\d+', salary[2])[0]

        elif len(salary) == 9: # ['200\xa0000', '\xa0', '—', '\xa0', '280\xa0000', '\xa0', 'руб.', '/', 'месяц']
            currency = re.findall(r'(\w{3}).$', salary[6])[0]
            min_salary = salary[0]
            max_salary = salary[4]

        return min_salary, max_salary, currency


class CastoramaPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_database = client.products

    def process_item(self, item, spider):
        print(item)
        collection = self.mongo_database[spider.product]
        collection.insert_one(item)
        return item


class CastoramaPhotosPipelin(ImagesPipeline):
    def get_media_requests(self, item, info):
        photos = item['photos']
        if photos:
            for img in photos:
                try:
                    yield scrapy.Request(img)
                except Exception as err:
                    print(err)
        return item

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        # print(request)
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        name_directory = item['product_name']
        return f'full/{name_directory}/{image_guid}.jpg'


class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_database = client.instagram

    def process_item(self, item, spider):
        # print(item)
        collection = self.mongo_database[item['profile_name']]
        del item['profile_name']
        collection.insert_one(item)
        return item

class InstagramPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        photo = item['follow_photo']
        if photo:
            try:
                yield scrapy.Request(photo)
            except Exception as err:
                print(err)

    def file_path(self, request, response=None, info=None, *, item=None):
        # image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        name_directory = item['profile_name']
        follow_username = item['follow_username']
        return f'full/{name_directory}/{follow_username}.jpg'


# {'follow_id': 4496800393,
#  'follow_name': 'Anastasia Belova',
#  'follow_photo': 'https://instagram.frix4-1.fna.fbcdn.net/v/t51.2885-19/246762978_4460381927370741_392426189970097762_n.jpg?stp=dst-jpg_s150x150&_nc_ht=instagram.frix4-1.fna.fbcdn.net&_nc_cat=109&_nc_ohc=7WgXGN1xSZsAX81cjik&edm=APQMUHMBAAAA&ccb=7-4&oh=00_AT9_HpHKcwPzwo-s3fC8YlR-Clff9yatrmKYDLZ0d7BWJg&oe=62781F93&_nc_sid=e5d0a6',
#  'follow_username': 'anastasiatrue',
#  'profile_name': 'geekbrains.ru',
#  'user_classification': 'follower'}