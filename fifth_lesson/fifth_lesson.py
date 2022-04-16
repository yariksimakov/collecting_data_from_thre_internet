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
from selenium.webdriver.common.action_chains import ActionChains
from pprint import pprint
import time

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
time.sleep(1) # Я так сделал чтобы не было ошибки ElementNotInteractableException - я так и не понял почему она возникает
# input_password = driver.find_element(By.NAME, 'password')
input_password.send_keys('NextPassword172#') # Error - selenium.common.exceptions.ElementNotInteractableException: Message: element not interactable
input_password.submit()

# driver.find_elements(By.XPATH, '//div[contains(@class, "ReactVirtualized__Grid__innerScrollContainer")]/a')
# scrolling = ActionChains(driver)
# scrolling.move_to_element(elem_letter[-1])
# scrolling.perform()

# driver.find_elements(By.XPATH, '//div[contains(@class, "ReactVirtualized__Grid")]/a')

link_list = []
data_id_set = set()
while True:
    # wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "ReactVirtualized__Grid__innerScrollContainer")]/a')))
    time.sleep(4)
    elem_letters = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "ReactVirtualized__Grid__innerScrollContainer")]/a')))
    driver.execute_script('arguments[0].scrollIntoView(true);', elem_letters[-1]) # Message: stale element reference: element is not attached to the page document
    time.sleep(1)
    for elem in elem_letters:
        elem_data_id = elem.get_attribute('data-id') # Message: stale element reference: element is not attached to the page document
        elem_href = elem.get_attribute('href')

        if elem_data_id not in data_id_set:
            data_id_set.add(elem_data_id)
            link_list.append(elem_href)

    if len(link_list) == 20:
        break


pprint(link_list)

# elem_letter.get_attribute('href')
# elem_letter[0].text
# elem_letter[0].find_element(By.XPATH, './/div[contains(@class, "DFBrIJS_DFBrILW")]').text


