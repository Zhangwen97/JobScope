#!/usr/bin/env python
# coding: utf-8

# Import Necessary Modules for Project

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import pandas as pd
import re


# Define Variables and Functions

#Create the browser for Selenium
browser = webdriver.Firefox(executable_path = '/Users/della/jupyter-workspace/geckodriver-v0.25.0-win64/geckodriver')
url_list = []

#Define List Variables for Glassdoor
#Overall Metrics
overall_list = []
recommend_to_friend_list = []
ceo_approval_list = []

#Detailed Metrics
culture_list = []
work_life_b_list = []
management_list = []
comp_list = []
career_ops_list = []


#Function Definitions
#Function for navigating to website of list of companies
def find_company_urls(company):
    search_term = 'glassdoor.com/Overview working at ' + company
    #Go to Google and search for term
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
    time.sleep(10)
    current_url = browser.current_url
    url_list.append(current_url)
    time.sleep(3)
    soup_main = BeautifulSoup(browser.page_source, 'html')
    find_overall_ratings(soup_main)
    browser.find_element_by_css_selector('.common__EIReviewsRatingsStyles__ratingsDetailsLink.link').click()
    soup_details = BeautifulSoup(browser.page_source, 'html')
    find_detailed_ratings(soup_details)
    time.sleep(3)

#Glassdoor Data Scraping Functions using BeautifulSoup
def find_overall_ratings(soup):
    soup_main = soup
    overall = soup_main.find('span', class_='rating')
    overall = str(overall)
    overall = overall[54:57]
    overall_list.append(overall)
    recommend_to_friend = soup_main.find('div', {'id': 'EmpStats_Recommend'}).contents
    recommend_to_friend = str(recommend_to_friend)
    recommend_to_friend = recommend_to_friend[705:708]
    recommend_to_friend_list.append(recommend_to_friend)
    ceo_approval = soup_main.find('div', {'id': 'EmpStats_Approve'}).contents
    ceo_approval = str(ceo_approval)
    ceo_approval = ceo_approval[705:708]
    ceo_approval_list.append(ceo_approval)
    
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
    
#Function for clearing bad character for Recommend to Friend and CEO Approval
def clean_lists(list):
    pat = r'<$'
    clean_list = [i[0:2] for i in list if re.search(pat, i) != None]
    return clean_list

#Login to Glassdoor with Selenium
def login():
    browser.get('https://www.glassdoor.com/profile/login_input.htm?userOriginHook=HEADER_SIGNIN_LINK')
    time.sleep(3)
    email = browser.find_element_by_id('userEmail')
    password = browser.find_element_by_id('userPassword')
    time.sleep(3)
    email.send_keys('jdellape@andrew.cmu.edu')
    password.send_keys('Python95888')
    time.sleep(5)
    browser.find_element_by_css_selector('.gd-ui-button.minWidthBtn.css-3b85b3').click()

#Establish the list of companies to gather data for. Use a txt file of Best Places to Work
path = "C:/Users/della/jupyter-workspace/Files/company_list.txt"
with open(path) as f:
    company_list = [x.rstrip() for x in f if x > ' ']

#Execute GlassDoor Login
login()

#Loop companies through data collection functions
for c in company_list:
    find_company_urls(c)

#Clean recommend_to_friend_list and ceo_approval_list
recommend_to_friend_list = clean_lists(recommend_to_friend_list)
ceo_approval_list = clean_lists(ceo_approval_list)


# Create Dataframe and export to csv
#Prep data for loading into a Pandas dataframe (df)
gd_data = {'Company Name': company_list, 'Overall Stars': overall_list,
          'Culture & Values': culture_list, 'Work/Life Balance': work_life_b_list,
          'Senior Management': management_list, 'Compensation & Benefits': comp_list, 'Career Opportunities': career_ops_list,
          'URL': url_list}

gd_df = pd.DataFrame(gd_data)

out_path = "glassdoor_data.csv"

gd_df.to_csv(out_path)




