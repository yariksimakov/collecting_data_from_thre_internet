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

# input_password = driver.find_element(By.NAME, 'password')
input_password.send_keys('NextPassword172#') # Error - selenium.common.exceptions.ElementNotInteractableException: Message: element not interactable
input_password.submit()

print()

# driver.find_elements(By.XPATH, '//a[contains(@class, "js-letter-list-item")]')
