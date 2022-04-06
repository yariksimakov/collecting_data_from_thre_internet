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
import re
import pandas as pd
from bs4 import BeautifulSoup as bs
from pprint import pprint
import requests as rqt


# https://spb.hh.ru/search/vacancy?area=2&fromSearchLine=true&text=python&page=0
# https://spb.hh.ru/search/vacancy?area=2&fromSearchLine=true&text=python&page=0&hhtmFrom=vacancy_search_list


position = input('Please enter your desired position: ')
page = int(input('Please enter page max: '))
base_url = 'https://spb.hh.ru'


def turn_pages(base, position='python', page=0):
    url = base + f'/search/vacancy?area=2&fromSearchLine=true&text={position}&page={page}&hhtmFrom=vacancy_search_list'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36'}
    response = rqt.get(url, headers=headers)
    dom = bs(response.text, 'html.parser')
    return dom


# with open('response.html', 'w', encoding='utf-8') as file:
#     file.write(response.text)
# with open('response.html', 'r', encoding='utf-8') as file:
    # file_html = file.read()


def create_vacancys_list(data_vacancys):
    vacancys_list = []
    for tag_vacancy in data_vacancys:
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
    return vacancys_list


vacancys_list = []
for val in range(page-1):
    dom = turn_pages(base_url, position, page=val)
    tag_vacancys = dom.find_all('div', {'class': 'vacancy-serp-item'})
    vacancys_list.extend(create_vacancys_list(tag_vacancys))
# pprint(vacancys_list)


def processing_salary(data_list):
    new_dict = {'salary_min': [],
                'salary_max': [],
                'currency': []}

    for value in data_list:
        salary = value['salary']
        if salary == None:
            new_dict['salary_min'].append(None)
            new_dict['salary_max'].append(None)
            new_dict['currency'].append(None)
        else:
            salary_split = re.split(r'(\d+\D\d+)', salary)
            if len(salary_split) == 3:
                if salary_split[0] == 'от ':
                    new_dict['salary_min'].append(int(salary_split[1].replace('\u202f', '')))
                    new_dict['salary_max'].append(None)
                    new_dict['currency'].append(salary_split[2])
                elif salary_split[0] == 'до ':
                    new_dict['salary_min'].append(None)
                    new_dict['salary_max'].append(int(salary_split[1].replace('\u202f', '')))
                    new_dict['currency'].append(salary_split[2])
            elif len(salary_split) == 5:
                new_dict['salary_min'].append(int(salary_split[1].replace('\u202f', '')))
                new_dict['salary_max'].append(int(salary_split[3].replace('\u202f', '')))
                new_dict['currency'].append(salary_split[4])
            else:
                new_dict['salary_min'].append(None)
                new_dict['salary_max'].append(None)
                new_dict['currency'].append(None)
    return new_dict

salarys_dict = processing_salary(vacancys_list)


def creat_dict_for_data_frame(data_list):
    new_dict = {}
    for key in data_list[0].keys():
        if key == 'salary':
            continue
        new_dict[key] = []

    for value_list in data_list:
        for key in value_list:
            if key == 'salary':
                continue
            new_dict[key].append(value_list[key])
    new_dict.update(salarys_dict)
    return new_dict

dict_for_data_frame = creat_dict_for_data_frame(vacancys_list)


vacancies_df = pd.DataFrame(dict_for_data_frame)
pprint(vacancies_df)
vacancies_df.to_csv('vacancies_to_work.csv', index=False, encoding='utf-8')


# Это я выяснял какое регулярное выражение написать
# re.split(r'(\d+\D\d+)', param_for_test)
# Out[64]: ['от ', '3\u202f000', ' USD']
# Out[68]: ['', '160\u202f000', ' – ', '300\u202f000', ' руб.']
# Out[70]: ['до ', '400\u202f000', ' руб.']
