from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['letters_of_mail']
collection = db.letters


pprint(list(collection.find({})))