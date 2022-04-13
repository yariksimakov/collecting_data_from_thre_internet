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
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36'}


# def request_and_write_response(url, headers, file_name):
#     response = rq.get(url, headers=headers)
#     with open(f'{file_name}.html', 'w', encoding='utf-8') as file:
#         file.write(response.text)
#
#
# def open_file_for_get_html(file_name):
#     with open(f'{file_name}.html', 'r', encoding='utf-8') as file:
#         news_html = file.read()
#     return news_html


# news mail
url = 'https://news.mail.ru/'

def get_data(dom_html, parser):
    return dom_html.xpath(parser)


def from_string_and_get_dict(news_html, **kwargs):
    dom = html.fromstring(news_html)
    temporary_dict = {}

    for key in kwargs.keys():
        temporary_dict[key] = get_data(dom, kwargs[key])
    return temporary_dict


def get_html_page(url_path):
    response = rq.get(url_path, headers=headers)
    return response.text


# //table//a/@href - link for base news
# One the page
# //span[@datetime]/@datetime - time
# //h1/text()' - news
# //a[contains(@class, "breadcrumbs__link")]/span/text() - source
# //a[contains(@class, "breadcrumbs__link")]/@href - link to source


html_base_page = get_html_page(url)
link_base = from_string_and_get_dict(html_base_page, link_with_base_page='//table//a/@href')
# pprint(link_base)


result_list_for_mail = []
for index in range(len(link_base['link_with_base_page'])):
    html_page = get_html_page(link_base['link_with_base_page'][index])
    pages_news = from_string_and_get_dict(html_page,
                                          news='//h1/text()',
                                          source='//a[contains(@class, "breadcrumbs__link")]/span/text()',
                                          link_to_source='//a[contains(@class, "breadcrumbs__link")]/@href',
                                          time_publication='//span[@datetime]/@datetime')
    result_list_for_mail.append(pages_news)

pprint(result_list_for_mail)

# news lenta
url = 'https://lenta.ru/'

# //a[contains(@class,"_topnews")]/@href - link
# //a[contains(@class,"_topnews")]//time/text() - time
# //a[contains(@class,"_topnews")]//span
# //a[contains(@class,"_topnews")]//h3

response = rq.get(url, headers=headers)
dom = html.fromstring(response.text)

result_list_for_lenta = []
source = 'lenta.ru'
for watch in dom.xpath('//a[contains(@class,"_topnews")]'):
    temporary_dict = {}
    temporary_dict['link_to_source'] = watch.xpath('./@href')
    if not re.match(r'https://\w+', temporary_dict['link_to_source'][0]):
        temporary_dict['link_to_source'] = ['https://lenta.ru' + temporary_dict['link_to_source'][0]]

    temporary_dict['news'] = watch.xpath('.//span/text()')
    if not watch.xpath('.//span/text()'):
        temporary_dict['news'] = watch.xpath('.//h3/text()')

    temporary_dict['time_publication'] = watch.xpath('.//time/text()')
    temporary_dict['source'] = [source]
    result_list_for_lenta.append(temporary_dict)

# pprint(result_list_for_lenta)


collection_lenta.delete_many({})
collection_mail.delete_many({})


def insert_into_db(collection, data_list):
    for val in data_list:
        collection.insert_one(val)


insert_into_db(collection_mail, result_list_for_mail)
insert_into_db(collection_lenta, result_list_for_lenta)

pprint(list(collection_lenta.find({})))
pprint(list(collection_mail.find({})))
print(len(list(collection_lenta.find({}))), len(list(collection_mail.find({}))), sep='\t')
