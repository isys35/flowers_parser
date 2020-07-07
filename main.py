from selenium import webdriver
import config
import time
import httplib2
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import re
import sys

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
    time.sleep(1)
    all_images_src = []
    while True:
        time.sleep(1)
        new_images = False
        images = driver.find_elements_by_css_selector('img.product ')
        for image in images:
            image_src = re.sub(r'_H_(\d)\.jpg', '_H_1.jpg', image.get_attribute('src'))
            if image_src not in all_images_src:
                print(image_src)
                new_images = True
                all_images_src.append(image_src)
                image_name = re.findall(r'(\d+_\d+_H_1.jpg)', image_src)[0]
                save_image(image_src, image_name)
        if not new_images:
            break
        time.sleep(1)
        html = driver.find_element_by_tag_name('html')
        for _ in range(5):
            html.send_keys(Keys.DOWN)


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
            time.sleep(.3)


if __name__ == '__main__':
    driver = webdriver.Firefox()
    action(login)
    action(select_group)
    action(select_stock)
    action(select_subgroup)
    action(get_info)
    driver.close()
