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
from datetime import datetime,date
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

item = ['대웅제약', '한미약품', '유한양행', '종근당']
word = {'대웅제약': '%B4%EB%BF%F5%C1%A6%BE%E0&sDate=', '한미약품': '%C7%D1%B9%CC%BE%E0%C7%B0',
        '유한양행': '%C0%AF%C7%D1%BE%E7%C7%E0', '종근당': '%C1%BE%B1%D9%B4%E7'}
# item = ['대웅제약']
# word = {'대웅제약': '%B4%EB%BF%F5%C1%A6%BE%E0&sDate='}
max = 67
address = 'C:/Users/User/Desktop/wordcloud/ver4/data/'


def medi_crawler(maxpage, query):
    # print("<%s>" % query)
    page = 1
    total = []
    while page < maxpage:
        url = 'http://www.medipana.com/news/news_list_new.asp?Page=' + str(page) + '&MainKind=A&NewsKind=106&vCount=20&vKind=1&sID=&sWord=' + word[query]
        req = requests.get(url)
        cont = req.content
        soup = BeautifulSoup(cont, 'html.parser')
        for urls in soup.select("div.totalNews > ul > li > a"):
            try:
                news_detail = get_article('http://www.medipana.com/'+urls['href'].replace('..', ''), query)
                total.append(news_detail)
            except Exception as e:
                continue
        page += 1
        print('%d / %d ' % (page, maxpage))
    return total


def get_article(n_url, it):
    news_detail = ['', '', '', '', '']
    breq = requests.get(n_url)
    bsoup = BeautifulSoup(breq.content, 'html.parser')
    
    news_detail[0] = '메디파나'

    news_detail[1] = n_url

    title = bsoup.select('div.newView > div.tit')[0].get_text().replace('\n', '')
    try:
        title = title.encode('latin-1').decode('cp949','ignore')
    except Exception as e:
        None
    news_detail[2] = title

    text = bsoup.select("div.newView > div.newsCon")[0].get_text().replace('   ', '')
    text = re.sub(r"\[[^)]*\]", '', text).replace('\t', '').replace('\n', '').strip()
    try:
        text = text.encode('latin-1').decode('cp949','ignore')
    except Exception as e:
        None
    news_detail[3] = text
    date = bsoup.select('div.infor > span.data')[0].get_text()[:10].replace('-', '.')

    news_detail[4] = date

    return news_detail


def excel_make(it, results):
    df = pd.DataFrame(results, columns=['press', 'link', 'title', 'article', 'date'])
    results = df.drop_duplicates('link', keep='last')
    try:
        results.to_csv('%s%s_medipanaresult.csv' % (address, it), index=False, encoding='cp949')
    except:
        results.to_csv('%s%s_medipanaresult.csv' % (address, it), index=False)


def today(query):
    # print("medipana <%s>" % query)
    page = 1
    check = False
    total = []
    while page < 2:
        url = 'http://www.medipana.com/news/news_list_new.asp?Page=' + str(page) + '&MainKind=A&NewsKind=106&vCount=20&vKind=1&sID=&sWord=' + word[query]
        req = requests.get(url)
        cont = req.content
        soup = BeautifulSoup(cont, 'html.parser')
        for urls in soup.select("div.totalNews > ul > li > a"):
            try:
                news_detail = get_article('http://www.medipana.com/'+urls['href'].replace('..', ''), query)
                if news_detail[4] not in [todaydate, checkdate]:
                    check = True
                    break
                # print(news_detail)
                total.append(news_detail)
            except Exception as e:
                continue
        page += 1
        if check:
            break
    return total


def addnews(it):
    try:
        df = pd.read_csv('%s%s_medipanaresult.csv' % (address, it),encoding='cp949')
    except:
        df = pd.read_csv('%s%s_medipanaresult.csv' % (address, it))
    results = pd.DataFrame(today(it), columns=['press', 'link', 'title', 'article', 'date'])
    total_results = pd.concat([results, df])
    total_results = total_results.drop_duplicates('link', keep='last')
    try:
        total_results.to_csv('%s%s_medipanaresult.csv' % (address, it), index=False,encoding='cp949')
    except:
        total_results.to_csv('%s%s_medipanaresult.csv' % (address, it), index=False)


def crawl():
    for it in item:
        filename = '%s%s_medipanaresult.csv' % (address, it)
        
        if os.path.isfile(filename):
            if (datetime.fromtimestamp(os.path.getmtime('%s%s_naverresult.csv' % (address, it))).strftime('%G%m%d')) == date.today().strftime('%G%m%d'):
                continue
            addnews(it)
        else:
            data = medi_crawler(max, it)
            excel_make(it, data)


crawl()