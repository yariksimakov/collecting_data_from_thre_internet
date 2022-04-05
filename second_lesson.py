# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы получаем должность)
# с сайтов HH(обязательно) и/или Superjob(по желанию).
#
# Приложение должно анализировать несколько страниц сайта (также вводим
# через input или аргументы). Получившийся список должен содержать в себе минимум:

# Наименование вакансии.
# Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
# Ссылку на саму вакансию.
# Сайт, откуда собрана вакансия.

# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть одинаковая
# для вакансий с обоих сайтов.
#
# Общий результат можно вывести с помощью dataFrame через
# pandas. Сохраните в json либо csv.

from bs4 import BeautifulSoup as bs
from pprint import pprint
import requests as rqt


# https://spb.hh.ru/search/vacancy?area=2&fromSearchLine=true&text=python&page=0
# https://spb.hh.ru/search/vacancy?area=2&fromSearchLine=true&text=python&page=0&hhtmFrom=vacancy_search_list

base_url = 'https://spb.hh.ru'
url = base_url + '/search/vacancy?area=2&fromSearchLine=true&text=python&page=0&hhtmFrom=vacancy_search_list'
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36'}

# response = rqt.get(url, headers=headers)
# with open('response.html', 'w', encoding='utf-8') as file:
#     file.write(response.text)

with open('response.html', 'r', encoding='utf-8') as file:
    file_html = file.read()

dom = bs(file_html, 'html.parser')

tag_vacancys = dom.find_all('div', {'class': 'vacancy-serp-item'})
# pprint(tag_vacancy)


vacancys_list = []
for tag_vacancy in tag_vacancys:
    vacancy_dict = {}
    name = tag_vacancy.find('a', {'class': 'bloko-link'}).getText()
    link = tag_vacancy.find('a', {'class': 'bloko-link'})['href']
    website = base_url

    salary = tag_vacancy.find('span', {'class': 'bloko-header-section-3'})
    if salary:
        salary = salary.text
    else:
        salary = None

    job = tag_vacancy.find('div', {'class': 'bloko-text', 'data-qa': "vacancy-serp__vacancy_snippet_responsibility"})
    if job:
        job = job.text
    else:
        job = None

    requirement = tag_vacancy.find('div', {'class': 'bloko-text', 'data-qa': "vacancy-serp__vacancy_snippet_requirement"})
    if requirement:
        requirement = requirement.text
    else:
        requirement = None

    # Я хотел схитрить, но не смог
    # key_tuple = ['name', 'salary', 'link', 'website', 'job', 'requirement']
    # value_tuple = [name, salary link, website, job, requirement]
    # for key, value in zip(key_tuple, value_tuple):
    #     vacancy_dict[str(value)] = value

    vacancy_dict['name'] = name
    vacancy_dict['salary'] = salary
    vacancy_dict['link'] = link
    vacancy_dict['website'] = website
    vacancy_dict['job'] = job
    vacancy_dict['requirement'] = requirement
    vacancys_list.append(vacancy_dict)

pprint(vacancys_list)





# re.search(r'^до', salary)
# re.search(r'^от.', salary)

# re.search(r'.+USD$', salary)
# руб.

# re.split(r' – ', salary)
# Out[92]: ['20\u202f000', '30\u202f000 ']
