# -*- coding: utf-8 -*-
# from konlpy.tag import Okt
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(),encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(),encoding='utf-8')
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
word = {'대웅제약': '%B4%EB%BF%F5%C1%A6%BE%E0&sDate=', '한미약품': '%C7%D1%B9%CC%BE%E0%C7%B0',
        '유한양행': '%C0%AF%C7%D1%BE%E7%C7%E0', '종근당': '%C1%BE%B1%D9%B4%E7'}
# item = ['대웅제약']
# word={'대웅제약': '%B4%EB%BF%F5%C1%A6%BE%E0&sDate='}
max = 46
address = 'C:/Users/User/Desktop/wordcloud/ver4/data/'


def dailypharm_crawler(maxpage, query):
    # print("<%s>" % query)
    page = 0
    total = []
    while page < maxpage:
        url = 'http://www.dailypharm.com/Users/News/NewsSearch.html?nPage=' + str(page) + '&dpsearch=' + word[query]
        req = requests.get(url)
        cont = req.content
        soup = BeautifulSoup(cont, 'html.parser',from_encoding='utf-8')
        for urls in soup.select("li.newsList > a"):
            try:
                news_detail = get_article('http://www.dailypharm.com/Users/News/'+urls['href'], query)
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
    n_url = n_url.replace('&dpsearch='+it,'')
    breq = requests.get(n_url)
    bsoup = BeautifulSoup(breq.content, 'html.parser',from_encoding='utf-8')

    news_detail[0] = '데일리팜'
    
    news_detail[1] = n_url

    title = bsoup.select('div.d_newsHead > div.d_newsTitle')[0].get_text().replace('   ', '').replace('\n', '')
    # try:
    #     title = title.encode('latin-1').decode('cp949','ignore')
    # except Exception as e:
    #     None
    news_detail[2] = title.strip()

    text = bsoup.select("div.d_newsContWrap > div.newsContents.font1")[0].get_text().replace('   ', '')
    text = re.sub(r"\[[^)]*\]", '', text).replace('\t', '').replace('\n', '').strip()
    # try:
    #     text = text.encode('latin-1').decode('cp949','ignore')
    # except Exception as e:
    #     None
    news_detail[3] = text

    date = bsoup.select('div.d_newsName_wrap > span.d_newsDate')[0].text[:10]
    news_detail[4] = date.replace('-','.')

    return news_detail


def excel_make(it, results):
    df = pd.DataFrame(results, columns=['press', 'link', 'title', 'article', 'date'])
    results = df.drop_duplicates('link', keep='last')
    if not os.path.exists('../data'):
            os.makedirs('../data')
    try:
        results.to_csv('%s%s_dailypharmresult.csv' % (address, it), index=False, encoding='cp949')
    except:
        results.to_csv('%s%s_dailypharmresult.csv' % (address, it), index=False)


def today(query):
    # print("dailypharm <%s>" % query)
    page = 0
    check = False
    total = []
    while page < 2:
        url = 'http://www.dailypharm.com/Users/News/NewsSearch.html?nPage=' + str(page) + '&dpsearch=' + word[query]
        req = requests.get(url)
        cont = req.content
        soup = BeautifulSoup(cont, 'html.parser')
        for urls in soup.select("li.newsList > a"):
            try:
                news_detail = get_article('http://www.dailypharm.com/Users/News/'+urls['href'], query)
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
        df = pd.read_csv('%s%s_dailypharmresult.csv' % (address, it), encoding='cp949')
    except:
        df = pd.read_csv('%s%s_dailypharmresult.csv' % (address, it))
    results = pd.DataFrame(today(it), columns=['press', 'link', 'title', 'article', 'date'])
    total_results = pd.concat([results, df])
    total_results = total_results.drop_duplicates('link', keep='last')
    try:
        total_results.to_csv('%s%s_dailypharmresult.csv' % (address, it), index=False, encoding='cp949')
    except:
        total_results.to_csv('%s%s_dailypharmresult.csv' % (address, it), index=False)    

def crawl():
    for it in item:
        filename = '%s%s_dailypharmresult.csv' % (address, it)
        
        if os.path.isfile(filename):
            addnews(it)
            if (datetime.fromtimestamp(os.path.getmtime('%s%s_naverresult.csv' % (address, it))).strftime('%G%m%d')) == date.today().strftime('%G%m%d'):
                continue
            addnews(it)
        else:
            data = dailypharm_crawler(max, it)
            excel_make(it, data)


crawl()