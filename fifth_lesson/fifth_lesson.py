# C:\Users\User\AppData\Local\Temp\Rar$EXa0.363

# Вариант I
# Написать программу, которая собирает входящие письма из своего или тестового почтового
# ящика и сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172#
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pymongo import MongoClient
from pprint import pprint
import re
import time

client = MongoClient('localhost', 27017)
db = client['letters_of_mail']
collection = db.letters

s = Service('chromedriver.exe')
driver = webdriver.Chrome(service=s)

driver.get('https://mail.ru/?from=logout&ref=main')
driver.find_element(By.CLASS_NAME, 'resplash-btn_mailbox-big').click()

wait = WebDriverWait(driver, 25)
wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[@class="ag-popup__frame__layout__iframe"]')))

iframe = driver.find_element(By.XPATH, '//iframe[@class="ag-popup__frame__layout__iframe"]')
driver.switch_to.frame(iframe)

wait = WebDriverWait(driver, 25)
input_username = wait.until(EC.presence_of_element_located((By.NAME, 'username')))

# input_username = driver.find_element(By.NAME, 'username')
input_username.send_keys('study.ai_172')
input_username.submit()

wait = WebDriverWait(driver, 25)
input_password = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
time.sleep(
    1)  # Я так сделал чтобы не было ошибки ElementNotInteractableException - я так и не понял почему она возникает
# input_password = driver.find_element(By.NAME, 'password')
input_password.send_keys('NextPassword172#')
input_password.submit()

link_of_letter = set()
while True:
    wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, '//div[contains(@class, "ReactVirtualized__Grid__innerScrollContainer")]/a')))
    elem_have_link = wait.until(EC.text_to_be_present_in_element_attribute(
        (By.XPATH, '//div[contains(@class, "ReactVirtualized__Grid__innerScrollContainer")]/a'), 'href', 'https:'))
    if not elem_have_link:
        continue

    time.sleep(1)
    elem_letters = wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, '//div[contains(@class, "ReactVirtualized__Grid__innerScrollContainer")]/a')))
    for elem in elem_letters:
        elem_href = elem.get_attribute('href')
        link_of_letter.add(elem_href)

    driver.execute_script('arguments[0].scrollIntoView(true)', elem_letters[-1])
    if len(link_of_letter) >= 20:
        break

# pprint(link_of_letter)


data_letters = []
for i, letter in enumerate(link_of_letter):
    data_dict = {}
    driver.get(letter)
    elem_text = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "thread")]')))
    text = elem_text.text.split('\n', 2)
    data_dict['header'] = text[0]
    data_dict['time_get'] = re.findall(r'[а-яё]+, \d+:\d+', text[1], re.I)[0]
    data_dict['author'] = text[1].replace(data_dict['time_get'], '')
    data_dict['text'] = text[2].replace('\nОтветить\nПереслать\nОтписаться от рассылки\nПрочитать письмо', '')
    data_letters.append(data_dict)
    if i == 11:
        break
# text = driver.find_element(By.XPATH, '//div[contains(@class, "thread")]').text
# pprint(data_letters)


for letter in data_letters:
    collection.insert_one(letter)

pprint(list(collection.find({})))
