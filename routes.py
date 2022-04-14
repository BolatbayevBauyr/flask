# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import send_file
from flask import send_from_directory
import logging
from flask import jsonify, render_template, redirect, request, url_for, session
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)
from werkzeug.utils import send_file

from app.base import blueprint



import requests
from bs4 import BeautifulSoup
import csv
import os
from app.base.module_locator import module_path
def path_locator():
   pass 

cwd = module_path(path_locator)
cwd = cwd.replace("/routes.py", "")
logging.error(cwd)

file = cwd + '/Production.csv'
HOST = 'https://enbek.kz/ru'
URL = 'https://enbek.kz/ru/search/vac?profobl%5B120%5D=120&passwd%5B1%5D=1&passwd%5B4%5D=4&passwd%5B2%5D=2&profobl%5B104%5D=104&profobl%5B111%5D=111&profobl%5B105%5D=105&profobl%5B118%5D=118&profobl%5B117%5D=117&profobl%5B103%5D=103&profobl%5B124%5D=124&profobl%5B101%5D=101&profobl%5B116%5D=116'
Headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 OPR/78.0.4093.186', 'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}
def get_html(url, params=None):
    r = requests.get(url, headers = Headers, params=params)
    return r
def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('li', class_='page')
    if pagination:
        return int(pagination[-1].get_text())
    else:
        return 1
def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='item-list')
    jobs = []
    for item in items:
        address = item.find_all('li', class_='location d-flex align-items-center me-lg-3')
        if len(address) > 0:
            address = item.find('li', class_='location d-flex align-items-center me-lg-3').get_text(strip=True)
        else:
            address = 'отсутствует'
        jobs.append({
            'Должность': item.find('div', class_='title').get_text(strip=True),
            'Зарплата': item.find('div', class_='price').get_text(strip=True),
            'Компания': item.find('ul', class_='list-unstyled d-lg-flex').get_text(strip=True),
            'Адрес': address,
            'Ставка': item.find('li', class_='time d-flex align-items-center me-lg-3').get_text(strip=True),
            'Опыт': item.find('li', class_='experience d-flex align-items-center').get_text(strip=True),
            'Дата': item.find('div', class_='right-content ms-auto').get_text(strip=True)
        })
    return jobs
def save_file(items, path):
    with open (path, 'w', newline='', encoding='utf8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Должность','Зарплата','Компания','Адрес','Ставка','Опыт', 'Дата'])
        for item in items:
            writer.writerow([item['Должность'], item['Зарплата'], item['Компания'], item['Адрес'], item['Ставка'],item['Опыт'], item['Дата']])
def parse():
    logging.error("test")

    html = get_html(URL)
    if html.status_code == 200:
        jobs = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count + 1):
            print(f'Парсинг Страницы {page} из {pages_count}...')
            html = get_html(URL, params={'page': page})
            jobs.extend(get_content(html.text))
        save_file(jobs, file)
    else:
        print('Error')




@blueprint.route('/getdata')
def getdata():
    parse()
    return send_from_directory(cwd, "Production.csv")



@blueprint.route('/')
def route_default():

    return "success"

    



@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('page-403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('page-404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('page-500.html'), 500
