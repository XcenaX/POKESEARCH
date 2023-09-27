import os, sys, time
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE','area.settings')
django.setup()

from polls.models import  New, User
from datetime import date, datetime
import requests
from bs4 import BeautifulSoup as BS
import csv
import json
import re
from django.utils import timezone

URL = "https://www.zakon.kz/news"
COMMENTS_URL = "https://zcomments.net/service/init/1"

def get_all_urls():  # функция для получения всех урлов новостей за сегодня                      
    r = requests.get(URL) 
    html = BS(r.content, 'html.parser') # получаем html страницы новостей
    urls = []
    for item in html.select('.cat_news_item'): # пробегаем циклом по блокам новостей
        data = item.contents
        if len(data) == 3: # если это не блок новости а дата
            continue 
        current_url = "https://www.zakon.kz/" + data[3].get("href") # получаем url новости                                      
        urls.append(current_url)            
    return urls

def parse_one_new(url): # функция парсит одну новость по ссылке       
    r = requests.get(url)    
    html = BS(r.content, 'html.parser')

    main_block = ""
    try:
        main_block = html.select('.fullnews')[0].contents
    except IndexError:
        return
    
    title = main_block[1].text # получаем заголовок    
    content = main_block[3].text # получаем
    img_url = "https:" + main_block[7].get('src')    
    pub_date = main_block[9].contents[1].text
    pub_time = pub_date.split(", ")[1]
    pub_date = datetime.today().strftime("%d-%m-%Y")
    pub_date += ", " + pub_time
    pub_date = datetime.strptime(pub_date, "%d-%m-%Y, %H:%M")    
    
    
    
    url_name = re.split("/|-", url)[4]    
    content += html.select('#initial_news_story')[0].text.replace("Больше новостей в Telegram-канале «zakon.kz». Подписывайся!", '')  # удаляем ненужный текст          
    current_new = New.objects.filter(title=title, content=content, img_url=img_url)    
    print(title + "\n")
    if len(current_new) == 0:
        new = New.objects.create(title=title, content=content, img_url=img_url, pub_date=timezone.now(), url_name=url_name)
        new.save() 
    else:
        print("это уже есть -> (" + title + ")")       

print("Получаем урлы...")

urls = get_all_urls()

print("Парсим новости...")
for url in urls:        
    parse_one_new(url)
    

print("Поздравляю!! Вы украли новости с другого сайта")
