# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pprint import pprint
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

