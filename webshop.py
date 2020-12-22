from selenium import webdriver
import config
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import re
import sys
import csv
import traceback

DATA_FILE_NAME = 'data.csv'


def action(func):
    action_completed = False
    while not action_completed:
        try:
            func()
            action_completed = True
        except Exception:
            print(traceback.format_exc())
            time.sleep(.3)


def login():
    driver.get('https://webshop.ozexport.nl/Shop/Account/LogOn')
    login_element = driver.find_element_by_id('UserName')
    login_element.send_keys(config.Webshop.LOGIN)
    pass_element = driver.find_element_by_id('Password')
    pass_element.send_keys(config.Webshop.PASS)
    btn = driver.find_element_by_id('LogInButton')
    btn.click()


def select_data():
    driver.get(f'https://webshop.ozexport.nl/Shop/?dt={date}')
    elements = driver.find_elements_by_css_selector('span.menuButton.menuList')
    for element in elements:
        if 'Всё' in element.text:
            element.click()
            break


def get_max_page():
    tr_elements = driver.find_elements_by_css_selector('tr.reg')
    while not tr_elements:
        tr_elements = driver.find_elements_by_css_selector('tr.reg')
        time.sleep(1)
    buttons_elements = driver.find_elements_by_css_selector('.button.tiny.pageButton')
    return int(buttons_elements[-1].text)

def parsing_data():
    tr_elements = driver.find_elements_by_css_selector('tr.reg')
    while not tr_elements:
        tr_elements = driver.find_elements_by_css_selector('tr.reg')
        time.sleep(1)
    for tr_element in tr_elements:
        image_element = tr_element.find_element_by_css_selector('.RowImage.imageURL')
        image_source = image_element.get_attribute('src')
        aviability_el = tr_element.find_element_by_css_selector('.ucgMainStockDiv')
        pack_el = tr_element.find_element_by_css_selector('div.colEmb')
        name_el = tr_element.find_element_by_css_selector('span.ucgMainOmsSpan')
        additioanal_name = tr_element.find_element_by_css_selector('span.ucgMainGrowerSpan')
        color_el = tr_element.find_element_by_css_selector('td.colColor.colCol.enableHighlight')
        s1_s2_el = tr_element.find_element_by_css_selector('p.enableTooltip')
        i_el = tr_element.find_element_by_css_selector('td.colS4.colS4.enableHighlight')
        q_el = tr_element.find_element_by_css_selector('div.colQualityValue')
        pb_el = tr_element.find_element_by_css_selector('td.colMin.enableHighlight')
        str_el = tr_element.find_element_by_css_selector('td.colCountry.colCnt.enableHighlight')
        buckets_el = tr_element.find_element_by_css_selector('td.colOrder.colOrd')
        buckets_el_splited = buckets_el.find_elements_by_css_selector('div')
        things_el = tr_element.find_element_by_css_selector('td.colOrder.colOrd2')
        things_el_splited = things_el.find_elements_by_css_selector('div')
        flower = Flower(photo=image_source,
                        availability=aviability_el.text,
                        pack=pack_el.text,
                        name=name_el.text,
                        color=color_el.text,
                        s1_s2=s1_s2_el.text,
                        i=i_el.text,
                        q=q_el.text,
                        pb=pb_el.text,
                        str=str_el.text,
                        buckets=' '.join([buckets_el_splited[0].text, buckets_el_splited[1].text]),
                        things=things_el_splited[0].text,
                        eur=float(things_el_splited[1].text),
                        additional_name=additioanal_name.text)
        flower.save_info()




def create_head_csv():
    with open(DATA_FILE_NAME, "a", newline="") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows([['Фото',
                            'Наличие',
                            'Упак',
                            'Наименование',
                            'Наим.(доп.)',
                            'Цвет',
                            'S1',
                            'S2',
                            'i',
                            'Q',
                            'PB',
                            'Стр.',
                            'Вёдра(EUR)',
                            'Штуки',
                            'EUR']])


def create_csv_file():
    with open(DATA_FILE_NAME, "w", newline="", encoding='utf8') as file:
        csv.writer(file)


class Flower:
    def __init__(self, photo, availability, pack, name, color, s1_s2, i, q, pb, str, buckets, things, eur, additional_name):
        self.availability = availability
        self.photo = photo
        self.pack = pack
        self.name = name
        self.color = color
        self.s1_s2 = s1_s2
        self.i = i
        self.q = q
        self.pb = pb
        self.str = str
        self.buckets = buckets
        self.things = things
        self.eur = eur
        self.additional_name = additional_name

    def save_info(self):
        if ' ' in self.s1_s2:
            s1 = self.s1_s2.split(' ')[0]
            s2 = self.s1_s2.split(' ')[1]
            data = [self.photo, self.availability, self.pack, self.name, self.additional_name, self.color, s1, s2, self.i, self.q,
                    self.pb, self.str, self.buckets, self.things.split(' ')[0], self.eur]
        else:
            data = [self.photo, self.availability, self.pack, self.name, self.additional_name, self.color, self.s1_s2, '', self.i, self.q,
                    self.pb, self.str, self.buckets, self.things, self.eur]
        try:
            print(data)
        except UnicodeEncodeError:
            pass
        with open(DATA_FILE_NAME, "a", newline="", encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerows([data])


if __name__ == '__main__':
    print('Пример даты: 31 августа 2020 - 20200831')
    date = input('Введите дату в формате: yyyymmdd:')
    options = Options()
    options.headless = False
    driver = webdriver.Firefox(options=options)
    create_csv_file()
    create_head_csv()
    action(login)
    action(select_data)
    max_page = get_max_page()
    page = 1
    while page != max_page+1:
        button = driver.find_element_by_css_selector(f'.button.tiny.pageButton.pageButton_{page}')
        button.click()
        action(parsing_data)
        page += 1
    driver.close()
