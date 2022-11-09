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


def yakup_crawler(maxpage, query):
    # print("<%s>" % query)
    page = 1
    # content > div.paging.tp_25 > div > p > a:nth-child(2)
    # 페이지 설정 새로 필요함
    maxpage_t = (int(maxpage) - 1) * 15 + 1  # 16= 2페이지 31=3페이지 46=4페이지 ...121=9페이지
    total = []
    while page < maxpage_t:
        url = "http://www.yakup.com/search/index.html?num_start=" + str(page) + "&keyword=&csearch_word=" + query + "&csearch_type=news&cs_scope=&mode=&pmode="
        req = requests.get(url)
        cont = req.content
        soup = BeautifulSoup(cont, 'html.parser')
        # content > div.listBoxType_6.tm_20 > ul > div:nth-child(8) > dl > dd > h6 > a
        for urls in soup.select("h6.h6Type1.floatleft > a"):
            try:
                # print('\nurls: ', urls['href'])
                news_detail = get_article('http://www.yakup.com/'+urls['href'], query)
                # print(news_detail)
                total.append(news_detail)
            except Exception as e:
                # print(e)
                continue
        page += 15
        print('%d / %d ' % (page, maxpage_t))
    return total


def get_article(n_url, it):
    news_detail = ['', '', '', '', '']
    breq = requests.get(n_url)
    bsoup = BeautifulSoup(breq.content, 'html.parser')
    
    news_detail[0] = '약업신문'

    news_detail[1] = n_url

    title = bsoup.select('div#content > h4.h4Type01')[0].get_text().replace('\n', '')
    try:
        title = title.encode('latin-1').decode('cp949','ignore')
    except Exception as e:
        None
    news_detail[2] = title
    # print(title)
    text = bsoup.select("div.bodyarea")[0].get_text().replace('   ', '').replace('트윗하기', '')
    text = re.sub(r"\[[^)]*\]", '', text).replace('\t', '').replace('\n', '').strip()
    try:
        text = text.encode('latin-1').decode('cp949','ignore')
    except Exception as e:
        None
    news_detail[3] = text
    # print(text)
    date = bsoup.select('div.clear.tp_5 > p > span')[0].get_text()[5:15].replace('-', '.')
    news_detail[4] = date
    # print(date)

    return news_detail


def excel_make(it, results):
    df = pd.DataFrame(results, columns=['press', 'link', 'title', 'article', 'date'])
    results = df.drop_duplicates('link', keep='last')
    try:
        results.to_csv('%s%s_yakupresult.csv' % (address, it), index=False, encoding='cp949')
    except:
        results.to_csv('%s%s_yakupresult.csv' % (address, it), index=False)


def today(query):
    # print("yakup <%s>" % query)
    page = 1
    check = False
    # content > div.paging.tp_25 > div > p > a:nth-child(2)
    total = []
    while page < 30:
        url = "http://www.yakup.com/search/index.html?num_start=" + str(page) + "&keyword=&csearch_word=" + query + "&csearch_type=news&cs_scope=&mode=&pmode="
        req = requests.get(url)
        cont = req.content
        soup = BeautifulSoup(cont, 'html.parser')
        # content > div.listBoxType_6.tm_20 > ul > div:nth-child(8) > dl > dd > h6 > a
        for urls in soup.select("h6.h6Type1.floatleft > a"):
            try:
                # print('\nurls: ', urls['href'])
                news_detail = get_article('http://www.yakup.com/'+urls['href'], query)
                # print(news_detail)
                if news_detail[4] not in [todaydate, checkdate]:
                    check = True
                    break
                # print(news_detail)
                total.append(news_detail)
            except Exception as e:
                # print(e)
                continue
        page += 15
        if check:
            break
    return total


def addnews(it):
    try:
        df = pd.read_csv('%s%s_yakupresult.csv' % (address, it),encoding='cp949')
    except:
        df = pd.read_csv('%s%s_yakupresult.csv' % (address, it))
    results = pd.DataFrame(today(it), columns=['press', 'link', 'title', 'article', 'date'])
    total_results = pd.concat([results, df])
    total_results = total_results.drop_duplicates('link', keep='last')
    try:
        total_results.to_csv('%s%s_yakupresult.csv' % (address, it), index=False,encoding='cp949')
    except:
        total_results.to_csv('%s%s_yakupresult.csv' % (address, it), index=False)


def crawl():
    for it in item:
        filename = '%s%s_yakupresult.csv' % (address, it)
        
        if os.path.isfile(filename):
            if (datetime.fromtimestamp(os.path.getmtime('%s%s_naverresult.csv' % (address, it))).strftime('%G%m%d')) == date.today().strftime('%G%m%d'):
                continue
            addnews(it)
        else:
            data = yakup_crawler(max, it)
            excel_make(it, data)

crawl()
