# Inputs - chromedriver_executable, fortune100.csv, company_urls_modified.csv
# Outputs - reviews_word_freq.csv, comparably_scores_all.csv, comparably_company_reviews_sample.csv, company_urls.csv
# Author - Rahul Bhaskaruni

from urllib.request import Request, urlopen
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
from bs4 import BeautifulSoup
import pandas as pd
from wordcloud import STOPWORDS 


chromedriver_executable = "chromedriver"

# get link through selenium 
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




#getComparablyInfoSingleCompany('google',chromedriver_executable)

#**************** Scrape for 100 companies ********************

## gets all URLs for the fortune 100 companies
# Uses hard-coded values - need to change
companyList = pd.read_csv("./fortune100.csv")
companyURLDict = dict()
for company in companyList['company'].values:
    print("Scraping for: " + company)
    companyURLDict[company] = getHTML(company,chromedriver_executable)
pd.DataFrame(list(companyURLDict.items()),columns=['company','url']).to_csv("company_urls.csv")


## uses the fortune 100 links from the previous cell get reviews for the companies
companyListModified = pd.read_csv('./company_urls_modified.csv')
reviewDict = dict()
for i in range(companyListModified.shape[0]):
    company = companyListModified['company'][i]
    print("Getting reviews for: " + company)
    companyLink = companyListModified['url'][i]
    try:
        print("link used: "+companyLink+"/reviews")
        reviewDict[company] = (getReviews(companyLink+"/reviews"))
    except: 
        reviewDict[company] = ["no reviews found or something went wrong"]
        continue
pd.DataFrame.from_dict(reviewDict,orient='index').T.to_csv('comparably_company_reviews_sample.csv')



## Uses the fortune 100 links to scrape culture and ceo scores 
cultureDict = dict()
ceoDict = dict()
for i in range(companyListModified.shape[0]):
    company = companyListModified['company'][i]
    companyLink = companyListModified['url'][i]
    html = companyLink
    req = Request(html, headers={'User-Agent': 'Mozilla/5.0'})
    overview = BeautifulSoup(urlopen(req).read(),"lxml")
    try:
        cultureDict[company] = overview.find('div',{"class":"letterGrade"}).contents
        ceoDict[company] = overview.find('span',{"class":"grade-text"}).contents
    except:
        cultureDict[company] = ['NA']
        ceoDict[company] = ['-1']
        continue
cultureDF = pd.DataFrame(cultureDict).T
ceoDF = pd.DataFrame(ceoDict).T



# Writing culture and ceo dataframes to disk
cultureDF = pd.DataFrame(cultureDict).T
ceoDF = pd.DataFrame(ceoDict).T
overview_scores = cultureDF.join(ceoDF,lsuffix='culture_score',rsuffix='ceo_score')
overview_scores.to_csv('comparably_scores_all.csv')



# STOPWORDS
additionalStopWords = ['company','thing','lot','work']
additionalStopWords = additionalStopWords + list(companyListModified['company'].values)
for word in additionalStopWords:
    STOPWORDS.add(word.lower())
# STOPWORDS



# generating word frequencies
word_freq = dict()
for company in reviewDict.keys():
    if('no reviews found or something went wrong' in reviewDict[company]):
        continue
    else:
        print("treating reviews of:" + company)
        all_reviews = ' '.join(reviewDict[company])
        # removing punctuation, trimming white spaces and lower case
        all_reviews = re.sub(r'\s+',' ',re.sub("[^A-Za-z0-9' ]",' ',all_reviews).strip()).lower()
        # taken from https://stackoverflow.com/questions/15435726/remove-all-occurrences-of-words-in-a-string-from-a-python-list
        removeFormula = '|'.join(STOPWORDS)
        regex = re.compile(r'\b('+removeFormula+r')\b', flags=re.IGNORECASE)
        single_string_review_cleaned = re.sub(r'\s+',' ',regex.sub("",all_reviews))
        reviews_word_list = pd.Series([i for i in single_string_review_cleaned.split(sep=' ') if len(i)>3])
        top_50_words = reviews_word_list.groupby(by=reviews_word_list).count().sort_values(ascending=False)[:51]
        word_freq[company] = top_50_words.to_dict()
    



pd.DataFrame(word_freq.keys(),word_freq.values()).to_csv('reviews_word_freq.csv')

