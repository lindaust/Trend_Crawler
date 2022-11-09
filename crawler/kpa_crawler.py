# -*- coding: utf-8 -*-
# from konlpy.tag import Okt
from ckonlpy.tag import Twitter
import pickle
from collections import Counter
import requests
import csv
import os
import re
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from wordcloud import WordCloud
import warnings
import time

warnings.filterwarnings("ignore")
now = datetime.now()
todaydate = now.strftime('%Y-%m-%d')
todaydate = todaydate.replace('-', '.')
checkdate = (now - relativedelta(days=1)).strftime('%Y-%m-%d')
checkdate = checkdate.replace('-', '.')

fl = open('fixed_korean_stopwords.csv', 'r', encoding='UTF8')
files = csv.reader(fl)
stopwords = []
for file in files:
    stopwords.extend(file)
stopwords = set(stopwords)

# item = ['대웅제약', '한미약품', '유한양행', '종근당', '우루사', '임팩타민', '베아제']
item = ['대웅제약', '한미약품', '유한양행', '종근당']
max = 67
address = 'C:/Users/User/Desktop/wordcloud/ver4/data/'


def kpa_crawler(maxpage, query):
    # print("<%s>" % query)
    page = 1
    total = []
    while page < maxpage:
        url = 'https://www.kpanews.co.kr/article/list.asp?page=' + str(page) + '&search_word=' + query
        req = requests.get(url)
        cont = req.content
        soup = BeautifulSoup(cont, 'html.parser')
        for urls in soup.select("div.lst_article1 > ul > li > a"):
            try:
                news_detail = get_article('https://www.kpanews.co.kr/article/'+urls['href'], query)
                total.append(news_detail)
            except Exception as e:
                # print(e)
                time.sleep(5)
                continue
        page += 1
        print('%d / %d ' % (page, maxpage))
    return total


def get_article(n_url, it):
    news_detail = ['', '', '', '', '']
    breq = requests.get(n_url)
    bsoup = BeautifulSoup(breq.content, 'html.parser')
    
    news_detail[0] = '약사공론'

    news_detail[1] = n_url

    title = bsoup.select('div.inr-c2 > p.h1')[0].get_text().replace('\n', '')
    try:
        title = title.encode('latin-1').decode('cp949','ignore')
    except Exception as e:
        None
    news_detail[2] = title

    text = bsoup.select("div.bbs_cont.inr-c2 > div")[0].get_text()
    text = re.sub(r"\[[^)]*\]", '', text).replace('\t', '').replace('\n', '').strip()
    try:
        text = text.encode('latin-1').decode('cp949','ignore')
    except Exception as e:
        None
    news_detail[3] = text

    date = bsoup.select('p.t1.t_date > span')[0].get_text()[:10].replace('-', '.')
    news_detail[4] = date
    return news_detail


def excel_make(it, results):
    df = pd.DataFrame(results, columns=['press', 'link', 'title', 'article', 'date'])
    results = df.drop_duplicates('link', keep='last')
    try:
        results.to_csv('%s%s_kparesult.csv' % (address, it), index=False, encoding='cp949')
    except:
        results.to_csv('%s%s_kparesult.csv' % (address, it), index=False)


def today(query):
    # print("kpa <%s>" % query)
    page = 1
    check = False
    total = []
    while page < 2:
        url = 'https://www.kpanews.co.kr/article/list.asp?page=' + str(page) + '&search_word=' + query
        req = requests.get(url)
        cont = req.content
        soup = BeautifulSoup(cont, 'html.parser')
        for urls in soup.select("div.lst_article1 > ul > li > a"):
            try:
                news_detail = get_article('https://www.kpanews.co.kr/article/'+urls['href'], query)
                if news_detail[4] not in [todaydate, checkdate]:
                    check = True
                    break
                # print(news_detail)
                total.append(news_detail)
            except Exception as e:
                # print(e)
                time.sleep(5)
                continue
        page += 1
        if check:
            break
    return total


def addnews(it):
    try:
        df = pd.read_csv('%s%s_kparesult.csv' % (address, it),encoding='cp949')
    except:
        df = pd.read_csv('%s%s_kparesult.csv' % (address, it))
    results = pd.DataFrame(today(it), columns=['press', 'link', 'title', 'article', 'date'])
    total_results = pd.concat([results, df])
    total_results = total_results.drop_duplicates('link', keep='last')
    try:
        total_results.to_csv('%s%s_kparesult.csv' % (address, it), index=False, encoding='cp949')
    except:
        total_results.to_csv('%s%s_kparesult.csv' % (address, it), index=False)    

def crawl():
    for it in item:
        filename = '%s%s_kparesult.csv' % (address, it)
        
        if os.path.isfile(filename):
            if (datetime.fromtimestamp(os.path.getmtime('%s%s_naverresult.csv' % (address, it))).strftime('%G%m%d')) == date.today().strftime('%G%m%d'):
                continue
            addnews(it)
        else:
            data = kpa_crawler(max, it)
            excel_make(it, data)


crawl()