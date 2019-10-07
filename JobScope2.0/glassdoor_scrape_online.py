#!/usr/bin/env python
# coding: utf-8

#Import the necessary libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from urllib.request import Request,urlopen
import re
from bs4 import BeautifulSoup
import pandas as pd
from urllib.request import Request, urlopen

from selenium import webdriver

from selenium.webdriver.common.keys import Keys
import requests

import re
from wordcloud import WordCloud, STOPWORDS

import matplotlib.pyplot as plt

import os

#Create List containers
#Overall Metrics
overall_list = []

#Detailed Metrics
culture_list = []
work_life_b_list = []
management_list = []
comp_list = []
career_ops_list = []

#list for capturing URLs
url_list = []

 

#This is the company name that will be passed from the user in Wen's main file
def find_company_glassdoor(company,chromedriver_executable):
    #Configure webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    browser = webdriver.Chrome(executable_path=chromedriver_executable,options=options)
    #Go to Google and search for term
    search_term = 'glassdoor.com/Overview working at ' + company
    browser.get('https://www.google.com')
    google_search_bar = browser.find_element_by_css_selector('.gLFyf.gsfi')
    google_search_bar.click()
    time.sleep(3)
    google_search_bar.send_keys(search_term)
    google_search_bar.send_keys(Keys.RETURN)
    time.sleep(3)
    #Click on first result
    results = browser.find_elements_by_xpath('//div[@class="r"]/a/h3')
    results[0].click()
    time.sleep(5)
    current_url = browser.current_url
    url_list.append(current_url)
    time.sleep(3)
    soup_main = BeautifulSoup(browser.page_source, 'html')
    find_overall_ratings(soup_main)
    browser.find_element_by_css_selector('.common__EIReviewsRatingsStyles__ratingsDetailsLink.link').click()
    soup_details = BeautifulSoup(browser.page_source, 'html')
    find_detailed_ratings(soup_details)
    time.sleep(3)
    print_gd_info()
    browser.close()
    
#Glassdoor Data Scraping Functions using BeautifulSoup
def find_overall_ratings(soup):
    soup_main = soup
    overall = soup_main.find('span', class_='rating')
    overall = str(overall)
    overall = overall[54:57]
    overall_list.append(overall)

    
def find_detailed_ratings(soup):
    soup_details = soup 
    detailed_ratings_table = soup_details.find('div', {'class': 'eiRatingsDetails'}).contents
    detailed_ratings_score = soup_details.find_all('div', {'class':'col-2 p-0 eiRatingTrends__RatingTrendsStyle__ratingNum'})
    detailed_ratings_score = str(detailed_ratings_score)
    culture = detailed_ratings_score[221:224]
    culture_list.append(culture)
    work_life_b = detailed_ratings_score[300:303]
    work_life_b_list.append(work_life_b)
    management = detailed_ratings_score[379:382]
    management_list.append(management)
    comp = detailed_ratings_score[458:461]
    comp_list.append(comp)
    career_ops = detailed_ratings_score[537:540]
    career_ops_list.append(career_ops)
    
def print_gd_info():
    print('Glassdoor Information:')
    print('Overall Star Rating: {:s}'.format(overall_list[0]))
    print('Culture & Values: {:s}'.format(culture_list[0]))
    print('Work/Life Balance: {:s}'.format(work_life_b_list[0]))
    print('Senior Management: {:s}'.format(management_list[0]))
    print('Compensation & Benefits: {:s}'.format(comp_list[0]))
    print('Find More Information At: {:s}'.format(url_list[0]))


 

def getHTML(company,chromedriver_executable):

    options = webdriver.ChromeOptions()

    options.add_argument('headless')

    options.add_argument('window-size=1920x1080')

    options.add_argument("disable-gpu")

    browser = webdriver.Chrome(executable_path=chromedriver_executable,options=options)

    browser.get("https://www.comparably.com")

    search_bar = browser.find_element_by_xpath('/html/body/div/div/div[1]/div/div/div/div[1]/div/div/form/div/div/input')

    search_bar.send_keys(company)

    search_bar.send_keys(Keys.RETURN)

    time.sleep(3)

    browser.find_element_by_xpath('/html/body/div/div/div/div/div[2]/div[1]/div/div[2]/a[1]/div/div/div[1]').click()

    return_this = (browser.current_url)

    browser.close()

    return return_this

 

# Getting reviews into a list

def getReviews(html):

    reviews = []

    while html != '':

        req = Request(html, headers={'User-Agent': 'Mozilla/5.0'})

        comparably = BeautifulSoup(urlopen(req).read(),"lxml")

        try:

            temp_reviews=comparably.find_all('p',{"class":"cppRH-review-quote"})

            for tag in temp_reviews:

                if tag.find('a') is None:

                    reviews+=tag.contents

                else:

                    reviews+=tag.find('a').contents

            html = comparably.find_all('a', {"class":"page"})[-1]['href']

        except:

            html=''

            reviews+=["no reviews found"]

    return reviews

 

# Getting culture and ceo rating

def getOverviewScores(html):

    req = Request(html, headers={'User-Agent': 'Mozilla/5.0'})

    overview = BeautifulSoup(urlopen(req).read(),"lxml")

    try:

        culture_grade = overview.find('div',{"class":"letterGrade"}).contents

        ceo_score = overview.find('span',{"class":"grade-text"}).contents

    except:

        culture_grade = ['NA']

        ceo_score = ['NA']

    return (culture_grade,ceo_score)

 

 

# Review Treatment - returns dictionary with word frequency

def reviewTreatment(reviews,company):

    additionalStopWords = ['company','thing','lot','work']

    additionalStopWords = additionalStopWords + [company]

    for word in additionalStopWords:

        STOPWORDS.add(word.lower())

    if('no reviews found or something went wrong' in reviews):

        return dict()

    else:

        all_reviews = ' '.join(reviews)

        # removing punctuation, trimming white spaces and lower case

        all_reviews = re.sub(r'\s+',' ',re.sub("[^A-Za-z0-9' ]",' ',all_reviews).strip()).lower()

        # taken from https://stackoverflow.com/questions/15435726/remove-all-occurrences-of-words-in-a-string-from-a-python-list

        removeFormula = '|'.join(STOPWORDS)

        regex = re.compile(r'\b('+removeFormula+r')\b', flags=re.IGNORECASE)

        single_string_review_cleaned = re.sub(r'\s+',' ',regex.sub("",all_reviews))

        reviews_word_list = pd.Series([i for i in single_string_review_cleaned.split(sep=' ') if len(i)>3])

        top_50_words = reviews_word_list.groupby(by=reviews_word_list).count().sort_values(ascending=False)[:51]

        return top_50_words.to_dict()

 

# Single Company Scrape Comparably

def getComparablyInfoSingleCompany(company,chromedriver_executable):

    html = getHTML(company,chromedriver_executable)

    reviews_single_company = getReviews(html+'/reviews')

    word_freq = reviewTreatment(reviews_single_company,company)

    culture_score, ceo_score = getOverviewScores(html)

    print("CEO Approval: " + (ceo_score[0] if ceo_score[0]!='NA' else "value unavailable"))

    print("Culture Grade: " + (culture_score[0] if culture_score[0]!='NA' else "value unavailable"))

    return (word_freq)


