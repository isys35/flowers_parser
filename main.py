from selenium import webdriver
import config
import time
import httplib2
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import re
import sys
import csv
import traceback

DATA_FILE_NAME = 'data.csv'

def login():
    driver.get('http://109.109.104.10/webshop2/Login.aspx?ReturnUrl=%2fwebshop2%2fVoorraad.aspx#voorcod=22&vrdgrp=20&celcod=ALL___&artgrpcod=ALL___')
    login_element = driver.find_element_by_id('cntBody_Login1_UserName')
    login_element.send_keys(config.LOGIN)
    pass_element = driver.find_element_by_id('cntBody_Login1_Password')
    pass_element.send_keys(config.PASS)
    btn = driver.find_element_by_id('cntBody_Login1_btnOk')
    btn.click()


def select_group():
    combobox = driver.find_element_by_id('cbVoorraadGroep')
    combobox_arrow = combobox.find_element_by_css_selector('div.combobox-buttons.trigger')
    combobox_arrow.click()
    group_li = driver.find_element_by_id('G20')
    group_a = group_li.find_element_by_css_selector('a')
    group_a.click()


def select_stock():
    combobox = driver.find_element_by_id('cbVoorraad')
    combobox_arrow = combobox.find_element_by_css_selector('div.combobox-buttons.trigger')
    combobox_arrow.click()
    stock_li = driver.find_element_by_id('V22')
    stock_a = stock_li.find_element_by_css_selector('a')
    stock_a.click()


def select_subgroup():
    combobox = driver.find_element_by_id('cbProductgroep')
    combobox_arrow = combobox.find_element_by_css_selector('div.combobox-buttons.trigger')
    combobox_arrow.click()
    stock_li = driver.find_element_by_id('PP100')
    stock_a = stock_li.find_element_by_css_selector('a')
    stock_a.click()


def get_info():
    time.sleep(5)
    all_images_src = []
    while True:
        time.sleep(1)
        new_images = False
        items = driver.find_elements_by_css_selector('.item.layout2.horizontaal ')
        for item in items:
            image = item.find_element_by_css_selector('img.product ')
            image_src = re.sub(r'_H_(\d)\.jpg', '_H_1.jpg', image.get_attribute('src'))
            if image_src not in all_images_src:
                new_images = True
                flower = get_flower(item, image_src)
                if flower:
                    all_images_src.append(image_src)
                    flower.save_info()
                # save_image(image_src, 'img/' + image_name)
        if not new_images:
            break
        time.sleep(1)
        html = driver.find_element_by_tag_name('html')
        html.send_keys(Keys.PAGE_DOWN)


def get_flower(item, image_src):
    name_block = item.find_element_by_css_selector('div.omschrijving')
    name = name_block.find_element_by_css_selector('a').text
    print(name)
    price = item.find_element_by_css_selector('.prijs').text
    info = {}
    trs = item.find_elements_by_css_selector('tr')
    for tr in trs:
        label = tr.find_element_by_css_selector('td.label').text
        if label == 'Страна производства':
            value = tr.find_element_by_css_selector('td.value').find_element_by_css_selector('img').get_attribute('title')
        else:
            value = tr.find_element_by_css_selector('td.value').text
        info[label] = value
    if len(info) < 9:
        return False
    else:
        print(info)
        return Flower(name=name, price=price, info=info, image_url=image_src)


def get_detal_info():
    detal_view = driver.find_element_by_id('detailView')
    big_image = detal_view.find_element_by_css_selector('img.product ')
    url_image = big_image.get_attribute('src')
    btn_close = driver.find_element_by_id('btnCloseWindow')
    btn_close.click()
    print(url_image)


def save_image(url, image_name):
    h = httplib2.Http('.cache')
    response, content = h.request(url)
    with open(f"{image_name}", 'wb') as out:
        out.write(content)


def action(func):
    action_completed = False
    while not action_completed:
        try:
            func()
            action_completed = True
        except Exception:
            print(traceback.format_exc())
            time.sleep(.3)


def create_csv_file():
    with open(DATA_FILE_NAME, "w", newline="", encoding='utf8') as file:
        csv.writer(file)


def create_head_csv():
    with open(DATA_FILE_NAME, "a", newline="") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows([['Наименование',
                            'Цена',
                            'Изображение',
                            'Количество тары',
                            'Количество штук в паллетке',
                            'Количество штук в наличии',
                            'код тары',
                            'Цвет',
                            'Диаметр горшка',
                            'Страна производства',
                            'Кол. бутонов ( мин)',
                            'Высота',
                            'Ov leveranciers-info',
                            'Производитель']])


class Flower:
    def __init__(self, name, price, info, image_url):
        self.name = name
        self.price = price
        self.info = info
        self.image_url = image_url

    def save_info(self):
        # save_image(self.image_url, self.image_path)
        data = [None for _ in range(14)]
        data[0] = self.name
        data[1] = self.price
        data[2] = self.image_url
        if 'Количество тары' in self.info.keys():
            data[3] = self.info['Количество тары']
        if 'Количество штук в паллетке' in self.info.keys():
            data[4] = self.info['Количество штук в паллетке']
        if 'Количество штук в наличии' in self.info.keys():
            data[5] = self.info['Количество штук в наличии']
        if 'код тары' in self.info.keys():
            data[6] = self.info['код тары']
        if 'Цвет' in self.info.keys():
            data[7] = self.info['Цвет']
        if 'Диаметр горшка' in self.info.keys():
            data[8] = self.info['Диаметр горшка']
        if 'Страна производства' in self.info.keys():
            data[9] = self.info['Страна производства']
        if 'Кол. бутонов ( мин)' in self.info.keys():
            data[10] = self.info['Кол. бутонов ( мин)']
        if 'Высота' in self.info.keys():
            data[11] = self.info['Высота']
        if 'Ov leveranciers-info' in self.info.keys():
            data[12] = self.info['Ov leveranciers-info']
        if 'Производитель' in self.info.keys():
            data[13] = self.info['Производитель']
        with open(DATA_FILE_NAME, "a", newline="") as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerows([data])


if __name__ == '__main__':
    options = Options()
    options.headless = True
    driver = webdriver.Firefox('/home/isysbas/flowers_parser/geckodriver', options=options)
    create_csv_file()
    create_head_csv()
    action(login)
    action(select_group)
    action(select_stock)
    # action(select_subgroup)
    action(get_info)
    driver.close()
