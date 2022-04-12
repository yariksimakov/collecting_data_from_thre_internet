# 1 Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru,
# lenta.ru, yandex-новости. Для парсинга использовать XPath. Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.
# 2 Сложить собранные новости в БД
# Минимум один сайт, максимум - все три
from pymongo import MongoClient
from lxml import html
from pprint import pprint
import requests as rq
import re

client = MongoClient('127.0.0.1', 27017)
db = client['news']
collection_mail = db.news_mail
collection_lenta = db.news_lenta

url = 'https://news.mail.ru/'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36'}


def request_and_write_response(url, headers, file_name):
    response = rq.get(url, headers=headers)
    with open(f'{file_name}.html', 'w', encoding='utf-8') as file:
        file.write(response.text)


def open_file_for_get_html(file_name):
    with open(f'{file_name}.html', 'r', encoding='utf-8') as file:
        news_html = file.read()
    return news_html


def from_string_get_data(news_html, parser_for_object, parser_for_link):
    dom = html.fromstring(news_html)
    object_list = dom.xpath(parser_for_object)
    link_object_list = dom.xpath(parser_for_link)
    return object_list, link_object_list


def from_string_get_time_for_mail(news_html, parser):
    dom = html.fromstring(news_html)
    time_object_list = dom.xpath(parser)
    return time_object_list


def generate_list_of_dict_for_db(site_name, news_list, link_list, time_list):
    result_list = []

    if len(news_list) == len(link_list) and len(link_list) == len(time_list):
        for index in range(len(news_list)):
            temporary_dict = {}
            temporary_dict['news'] = news_list[index]
            temporary_dict['site name'] = site_name
            temporary_dict['link for news'] = link_list[index]
            temporary_dict['time publication '] = time_list[index]
            result_list.append(temporary_dict)
    else:
        raise IndexError('You have entered  asymmetric length lists')

    return result_list


# news.mail.ru - https://news.mail.ru/
# base news
# //table//td[position()<3]//span/span - text
# //table//td[position()<3]//a/@href - link
# //div[contains(@class, " breadcrumbs_article breadcrumbs_multiline")]/span[1]/span - time


# request_and_write_response(url, headers, 'mail_news')

# I get news and i get links for news
mail_news_html = open_file_for_get_html('mail_news')
news_object_mail, link_object_mail = from_string_get_data(mail_news_html, '//table//td[position()<3]//span/span/text()',
                                                          '//table//td[position()<3]//a/@href')

# I get date time of news
time_list_mail = []
for link in link_object_mail:
    response_html = rq.get(link_object_mail[0]).text
    time_object_mail = from_string_get_time_for_mail(response_html,
                                                     '//div[contains(@class, " breadcrumbs_article breadcrumbs_multiline")]/span[1]//span[contains(@class, "note__text")]/@datetime')
    time_list_mail.extend(time_object_mail)

# I processing news for data base
news_object_mail[0] = news_object_mail[0] + '. ' + news_object_mail[1]
news_object_mail.pop(1)

print(news_object_mail, link_object_mail, time_list_mail, sep='\n')
print(len(news_object_mail), len(link_object_mail), len(time_list_mail), sep='\n')

list_of_dict_for_db_mail = generate_list_of_dict_for_db('mail_news', news_object_mail, link_object_mail, time_list_mail)

# news lenta
# //div[@class="topnews"]/div[@class="topnews__column"]//h3 - text
# //div[@class="topnews"]/div[@class="topnews__column"]//div[@class="card-big__info"]/time - time for h3
# //div[@class="topnews"]/div[@class="topnews__column"]//div[@class="card-mini__info"]/time - time
# //div[@class="topnews"]/div[@class="topnews__column"]//span - text
# //div[@class="topnews"]/div[@class="topnews__column"]//a - link

# request_and_write_response('https://lenta.ru/', headers, 'lenta')

lenta_html = open_file_for_get_html('lenta')

# I get data for first news
dom = html.fromstring(lenta_html)
news_object_lenta = dom.xpath('//div[@class="topnews"]/div[@class="topnews__column"]//h3/text()')
time_list_lenta = dom.xpath(
    '//div[@class="topnews"]/div[@class="topnews__column"]//div[@class="card-big__info"]/time/text()')

object_list_lenta_2, link_object_lenta = from_string_get_data(lenta_html,
                                                              '//div[@class="topnews"]/div[@class="topnews__column"]//span/text()',
                                                              '//div[@class="topnews"]/div[@class="topnews__column"]//a/@href')
time_list_2 = dom.xpath(
    '//div[@class="topnews"]/div[@class="topnews__column"]//div[@class="card-mini__info"]/time/text()')

# I processing link for news of lenta
news_object_lenta.extend(object_list_lenta_2)
time_list_lenta.extend(time_list_2)
for index, val in enumerate(link_object_lenta):
    bool_link = re.match(r'https://\w+', val)
    if not bool_link:
        link_object_lenta[index] = 'https://lenta.ru' + val

print(news_object_lenta, link_object_lenta, time_list_lenta, sep='\n')
print(len(news_object_lenta), len(link_object_lenta), len(time_list_lenta), sep='\n')

list_of_dict_for_db_lenta = generate_list_of_dict_for_db('lenta', news_object_lenta, link_object_lenta, time_list_lenta)

collection_lenta.delete_many({})
collection_mail.delete_many({})


def insert_into_db(collection, data_list):
    for val in data_list:
        collection.insert_one(val)


insert_into_db(collection_mail, list_of_dict_for_db_mail)
insert_into_db(collection_lenta, list_of_dict_for_db_lenta)

pprint(list(collection_lenta.find({})))
pprint(list(collection_mail.find({})))
# <pymongo.cursor.Cursor object at 0x0000003E99BC21C0>
# <pymongo.cursor.Cursor object at 0x0000003E99BC21C0>
print(len(list(collection_lenta.find({}))), len(list(collection_mail.find({}))), sep='\t')
