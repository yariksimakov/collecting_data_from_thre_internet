# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, которая
# будет добавлять только новые вакансии/продукты в вашу базу.
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше
# введённой суммы (необходимо анализировать оба поля зарплаты). Для тех, кто выполнил задание с
# Росконтролем - напишите запрос для поиска продуктов с рейтингом не ниже введенного или качеством не ниже
# введенного (то есть цифра вводится одна, а запрос проверяет оба поля)
from pymongo import MongoClient
from pprint import pprint
from pymongo.errors import DuplicateKeyError
import pandas as pd
import json


client = MongoClient('localhost', 27017)
db = client['vacancys_database']
collection = db.vacancys


vacancys_df = pd.read_csv('vacancies_to_work.csv')
parser = vacancys_df.to_json(orient='records')
vacancys_json = json.loads(parser)


def insert_to_collection(param_dict):
    name_list = []

    for value in param_dict:

        if value['name'] not in name_list:
            name_list.append(value['name'])
            try:
                collection.insert_one(value)
            except DuplicateKeyError('Duplicate key error') as err:
                pprint(err)

insert_to_collection(vacancys_json)

param_salary = int(input('Please enter a number: '))
def show_db_by_salary(param):
    for val in collection.find({'$or': [
                                {'salary_min': {'$gt': param}},
                                {'salary_max': {'$lte': param}},
                                {'salary_max': {'gt': param}}
                            ]}):
        pprint(val)

show_db_by_salary(param_salary)

