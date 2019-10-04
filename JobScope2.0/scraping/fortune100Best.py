import urllib.request
from lxml import etree
import pandas as pd
import re


'''
This program scraped 100 companie's information from FORTUNE 100 BEST COMPANIES TO WORK FOR, 
and store everything into a csv file
'''

url = "https://www.greatplacetowork.com/best-workplaces/100-best/2019"

#use chrome to open the website
page_info = urllib.request.urlopen(url).read().decode('utf-8')
#print(page_info)
html0=etree.HTML(page_info)

best100=[]
for i in range(1,101):#101
    address = html0.xpath ('//*[@id="list-detail-left-column"]/div[%d]/div[1]/a[2]/@href'%i)  # a list
    best100.append(address)

#print(best100)
rankid=1
df=pd.DataFrame(columns=['indicator1','indicator2','indicator3','indicator4','indicator5','indicator6','impressions_for_wordcloud'])
for cmpny in best100:
    page_info = urllib.request.urlopen (cmpny[0]).read ().decode ('utf-8')
    #print(cmpny[0])
    html = etree.HTML (page_info)

    # company and indicators
    name = html.xpath ('//*[@id="profile-header"]/div/div[2]/div[1]/div[2]/div/h1/text()')  # a list
    great = html.xpath ('//*[@id="profile-experience"]/div/div[2]/div/div/div[2]/text()')
    others = html.xpath ('//div[@id="experience-figures"]/div/div/text()')
    words = html.xpath ('//section[@id="profile-word-cloud-js"]//*[@type="text/javascript"]/text()')

    extracted_string = words[0]
    temp1 = re.findall (r"[\s\S]*var list = JSON.parse\(\'(.*)\'\)", extracted_string)[0][2:-2]
    temp2 = temp1.split ("],[")
    file = {}
    for temp in temp2:
        word = temp.split (',')[0][1:-1] + " "
        frequency = int (temp.split (',')[1][1:-1])
        file [word]= frequency

    dict = {}
    dict['company'] = name[0]
    dict['indicator1'] = great[0] + ' Employees say this is a great place to work'
    dict['indicator2'] = str (others[0]) + str (" ") + str (others[1])
    dict['indicator3'] = str (others[2]) + str (" ") + str (others[3])
    dict['indicator4'] = str (others[4]) + str (" ") + str (others[5])
    dict['indicator5'] = str (others[6]) + str (" ") + str (others[7])
    dict['indicator6'] = str (others[8]) + str (" ") + str (others[9])
    dict['impressions_for_wordcloud'] = str(file)

    cmpny_line = pd.DataFrame (dict,index=[rankid])
    rankid+=1
    df=pd.concat([df,cmpny_line])

df.to_csv ('fortune100.csv')
