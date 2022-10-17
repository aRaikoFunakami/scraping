from cgitb import html
import datetime
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome import service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert

import time
import pandas as pd
import feedparser
import re
import json
import base64
import sys



# config file by args[1]
args = sys.argv
CONFIG_FILE=args[1]

# login URL/ID/PASS
with open(CONFIG_FILE, 'r') as file:
    login = json.load(file)

USER = login['user']
PASS = login['password']
URL = login['url']
CHROME_DRIVER = login['chrome_driver']

# Web Driver
browser = webdriver.Chrome(CHROME_DRIVER)
browser.implicitly_wait(1)

# login to acs_mine
browser.get( URL)
time.sleep(1)

e = browser.find_element(By.ID, "username")
e.clear()
e.send_keys(USER)

e = browser.find_element(By.ID, "password")
e.clear()
e.send_keys(PASS)

e = browser.find_element(By.ID, "login-submit")
e.submit()

# wait for screen transition
time.sleep(1)

# load RSS informaiton
rss_url = browser.find_element(By.XPATH,'/html/body/div[1]/div[2]/div[1]/div[3]/div[2]/p[2]/span/a').get_attribute('href')

# feedparser.parse() cannot load a xml-file with ID/PASS
# get xml-file by browser and send it to feedparser
browser.get(rss_url)
xml=browser.find_element(By.XPATH,'/html/body/pre').text
d = feedparser.parse(xml)

# get list within 7days
titles = []
for e in d['entries']:
    updated_day = datetime.datetime.strptime(e['updated'],'%Y-%m-%dT%H:%M:%SZ')
    author_name = re.sub('\(.+\)', '', e['author'])
    if updated_day >  datetime.datetime.now() + datetime.timedelta(days=-7):
        titles.append({'updated':updated_day, 'author':author_name, 'title': e['title'], 'url': e['link']})

# making html and display it
if len(titles) <= 0:
    s = 'no update'
else:
    s='<html>'
    for e in titles:
        s = s + str(e['updated']) + ' ' + e['author'] + '　<a href="' + e['url'] + '">' + e['title'] + '</a> <br>' + "\n" 
    s=s+'</html>'

print(s)

s='data:text/html;charset=utf-8;base64,'+base64.b64encode(s.encode()).decode()
browser.get(s)

# close automatically
time.sleep(30)
browser.quit()
