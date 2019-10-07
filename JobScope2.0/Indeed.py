#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 15:46:53 2019

@author: ztjin
"""

#from selenium import webdriver

from selenium import webdriver
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import pandas as pd
import numpy as np
import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os
import warnings
import platform
warnings.filterwarnings("ignore")

#Comapny rates data& Salary data from Indeed
#Zhetian JIn

def get_link(com_url):
    html = urlopen(com_url)
    bysc = BeautifulSoup(html.read(), "lxml")
    return bysc
    
def get_rate(company_name):
    com_url = driver.current_url
    bysc = get_link(com_url)
    #get category scores
    category_list = bysc.findAll("div",{"class":"cmp-ReviewCategories-category"})
    #get average scores
    average_span = bysc.findAll("span", {"class":"cmp-average-rating"})
    average_rate = float(average_span[0].contents[0])
    #get scores dataframe
    cnt = 0
    rate_list = []
    cate_list = []
    for i in category_list:
        for j in i.children:
            if (cnt%3 == 0):
                rate_list.append(j.contents[0])
            elif(cnt%3 == 2):
                cate_list.append(j.contents[0])
            cnt += 1
        
    review_span = bysc.findAll("a", {"data-tn-element":"reviews-viewAllLink"})
    rate_cnt = int(review_span[0].contents[0].split(' ')[2].replace(',',''))
    #get category df
    rate_summary = pd.DataFrame([[float(i) for i in rate_list]],columns = cate_list)
    rate_summary['company'] = company_name
    #get other features
    #rate_summary['rate_cnt'] = rate_cnt
    #rate_summary['average_rate'] = average_rate
    
    return rate_summary
    
#disposed
def get_salary(name):
    com_url = 'https://www.indeed.com/cmp/'+ name +'/salaries'
    bysc = get_link(com_url)
    salary_tables = bysc.findAll('table', {"class" : "cmp-salary-table"})
    salary_collection = pd.DataFrame()
    for table in salary_tables:
        for tr in table.findAll('tr',{"class" : "cmp-salary-aggregate-table-entry cmp-sal-separate-row"}):

            position_title = tr.findAll('div', {"class" : "cmp-sal-title"})[0].contents[0].contents[0]
            reports_cnt = tr.findAll('div', {"class" : "cmp-sal-note"})[0].contents[0].replace(',','').split(' ')[0]
            salary_average = tr.findAll('strong', {"class" : "cmp-salary-amount"})[0].contents[0].replace(',','').strip('$')
            if len(tr.findAll('div', {"class" : "cmp-sal-min cmp-sal-caption cmp-float-left"})) != 0:
                salary_low = tr.findAll('div', {"class" : "cmp-sal-min cmp-sal-caption cmp-float-left"})[0].span.contents[0].replace(',','').strip('$')
                salary_high = tr.findAll('div', {"class" : "cmp-sal-max cmp-sal-caption cmp-float-right"})[0].span.contents[0].replace(',','').strip('$')
            else:
                salary_low = 0
                salary_high = 0
            position = pd.DataFrame({"Title":[position_title], "Reports":[reports_cnt], "Salary_AVG":[salary_average], "Salary_MIN":[salary_low], "Salary_MAX":[salary_high]}, index = [name])
            position["Company_Name"] = name
            salary_collection = salary_collection.append(position)
            
    return salary_collection
    



#define a function to get reviews
def extract_reviews(rates, titles, positions, times, review_text):
    #all the reviews on one page
    review_panels = driver.find_element_by_id("cmp-page")\
                            .find_element_by_class_name("cmp-center-container-wrapper")\
                            .find_element_by_class_name("cmp-center-container")\
                            .find_element_by_id("cmp-content")\
                            .find_elements_by_class_name("cmp-review-container")
                            
    for item in review_panels:
        #headings contain rate score, title, location
        review_heading = item.find_element_by_class_name("cmp-review-heading")
        review_rate = review_heading.find_element_by_class_name("cmp-ratings").find_element_by_class_name("cmp-ratingNumber").text
        review_title = review_heading.find_element_by_class_name("cmp-review-title").find_element_by_tag_name("span").text
        review_position = review_heading.find_element_by_class_name("cmp-review-subtitle").find_element_by_class_name("cmp-reviewer-job-title").text
        review_time = review_heading.find_element_by_class_name("cmp-review-subtitle").find_element_by_class_name("cmp-review-date-created").text
        #body part contains review
        review = item.find_element_by_class_name("cmp-review-content-container").text
        #use global variables, not rigorous though
        rates.append(review_rate)
        titles.append(review_title)
        positions.append(review_position)
        times.append(review_time)
        review_text.append(review)


#disposed
def show_wordcloud(review_text):
    wordcloud = WordCloud(stopwrods = STOPWORDS).generate(" ".join(review_text))
    plt.imshow(wordcloud)
    
    
    
#company's rates data along the time
def show_trend(company, company_name):
    #transfer to monthly data
    company['times'] = pd.to_datetime(company['times'])
    company['times'] = company['times'].apply(lambda x: x - datetime.timedelta(x.day))
    #convert string rates to numeric
    company['rates'] = company['rates'].astype('float')
    trend = company.groupby(['times']).mean()
    trend_cnt = company.groupby(['times']).count()
    
    
    plt.subplot(2,1,1)
    plt.plot(trend['rates'], 'o-', linewidth = 2)
    plt.title("The trend of " + company_name+ " monthly average rates & review count(Data from Indeed)")
    plt.ylabel("Average Rate")
    
    plt.subplot(2,1,2)
    plt.plot(trend_cnt['rates'], 'o-', linewidth = 2)
    plt.xlabel("Time(month)")
    plt.ylabel("Number of Reviews")
    
    plt.show()
    #trend.plot()

    

def show_radar(company_name, values, features = ['Work/Life Balance', 
                                   'Compensation/Benefits', 
                                   'Job Security/Advancement',
                                   'Management', 
                                   'Culture']):
    
    N = len(values)
    angles = np.linspace(0, 2*np.pi, N, endpoint = False)
    
    values = np.concatenate((values, [values[0]]))
    angles = np.concatenate((angles, [angles[0]]))


    fig = plt.figure()
    #111 stands for circle axis
    ax = fig.add_subplot(111, polar = True)
    
    ax.plot(angles, values, 'o-', linewidth = 2)
    ax.fill(angles, values, alpha = 0.25)
    #Add feature names
    ax.set_thetagrids(angles * 180/np.pi, features)
    ax.set_ylim(0, 5)
    plt.title(company_name+ "'s five indicators(Data from Indeed)")
    ax.grid(True)
    plt.show()
    
    
def main(company_name):
    #when request a 
    #driver = webdriver.Chrome("/Users/ztjin/Documents/Setting/chromedriver")
    #link to one company
    #driver.get("https://www.indeed.com/cmp/" + company_name + "/reviews")
    search_url(company_name)
    #initialize the list
    rates = []
    titles = []
    positions = []
    times = []
    review_text = []
    
    #First extract the first page(do...while...)
    extract_reviews(rates, titles, positions, times, review_text)
    #Then if there is a "Next" page, then get another page's review
    cnt = 0
    #at most 20 pages, or too slow
    while driver.find_elements_by_link_text("Next") != [] and cnt < 20:
        extract_reviews(rates, titles, positions, times, review_text)
        #choose the exact button
        button = driver.find_element_by_id("cmp-page")\
                        .find_element_by_class_name("cmp-center-container-wrapper")\
                        .find_element_by_class_name("cmp-center-container")\
                        .find_element_by_id("cmp-content")\
                        .find_element_by_class_name("cmp-Pagination")\
                        .find_element_by_link_text("Next")
        button.click()
        cnt += 1
        
    company = pd.DataFrame({'rates':rates, 
                            'titles':titles, 
                            'positions':positions, 
                            'times':times, 
                            'text':review_text})
    company['company'] = company_name
    return company

def search_url(company_name):

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    global driver
    if platform.system() == "Windows":
        driver = webdriver.Chrome("chromedriver.exe",options = options)
    elif platform.system() == "Darwin":
        driver = webdriver.Chrome("chromedriver", options = options)


    #link to one company
    driver.get("https://www.indeed.com/companies?from=gnav-jobsearch--jasx")
    search_box = driver.find_element_by_id("exploreCompaniesWhat")
    search_box.send_keys(company_name)
    search_button = driver.find_element_by_tag_name("button")
    search_button.click()
    #while driver.find_elements_by_class_name("clearfix cmp-CompanyWidget") != []:
    driver.find_element_by_id("cmp-discovery")\
            .find_element_by_css_selector("div.cmp-discovery-main.cmp-discovery-curated.clearfix")\
            .find_element_by_class_name("cmp-SearchResultContainer")\
            .find_element_by_class_name("cmp-CompanyListWidget")\
            .find_element_by_class_name("cmp-CompanyWidget-name").click()
    
    #click the review button
    driver.find_elements_by_class_name("cmp-MenuItem-link.cmp-u-noUnderline")[2].click()
    
    return driver.current_url
    
def indeed(company_name):
    #settings for plt
    #plt.rcParams['font.sans-serif'] = 'Microsoft YaHei'
    plt.rcParams['axes.unicode_minus'] = False
    
    review_file_name = "Indeed_review.csv"
    rate_file_name = "Indeed_rate.csv"
    
            
    try:
        #show trend, check file existance first
        if os.path.exists(review_file_name):
            company = pd.read_csv(review_file_name)
            del company[company.columns[0]]
            if company_name in set(company['company']):
                show_trend(company[company['company'] == company_name], company_name)
            else:
                pass
                # append a new record
                # pass
        #create review file
        else:
            company = main(company_name)
            company.to_csv(review_file_name, mode = 'a',  header = True)
            
        #show radar, check file existance first
        if os.path.exists(rate_file_name):
            rates = pd.read_csv(rate_file_name)
            if company_name in set(rates['company']):
                company_rates = rates[rates['company'] == company_name]
                del company_rates[company_rates.columns[0]]
            else:
                pass
        #create review file
        else:
            company_rates = get_rate(company_name)
            company_rates.to_csv(rate_file_name, mode = 'a' , header = True)
            
        value = list(company_rates.iloc[0, 0:5])
        show_radar(company_name, value)
    
    except Exception as e:
        print("Sorry we couldn't find such company")
    
    
if __name__ == '__main__':
    company_name = input("Enter the company you want to search:").capitalize()
    indeed(company_name)
    
    
        
        
        

    