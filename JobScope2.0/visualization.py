from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import imageio
import numpy as np

fortune_data = pd.read_csv ('fortune100.csv')
fortune_df = pd.DataFrame (fortune_data).rename (columns={"Unnamed: 0": "rankID"})

#Once user enters the right ID & password, the program starts
def startFunctions():
    print("\nHome")
    print ("1. Explore 2019 Fortune 100 Best Companies to Work For")
    print ("2. To be explored...")

    mainfunctionID = input ("\nPlease enter the function ID that you are interested in: ")
    if (mainfunctionID == "1"):
        fortuneHundred ()
    else:
        print("Please wait. Our programmers are working really hard!")



#show "2019 Fortune 100 Best Companies to Work For" List
def fortuneHundred():
    print("This is : 2019 Fortune 100 Best Companies to Work For\n")
    print(fortune_df[['rankID','company']].to_string(index=False))#use to_string(index=False) to hide the index
    print("\n1. Explore more into a specific company in this list:")
    print("2. Explore more into the whole list:")
    print("0. Go back to Home Page:")
    print("\nPlease enter the function ID that you are interested in: ")
    functionID=input()
    if(functionID=="1"):
        fortuneOne()
    elif(functionID=="2"):
        fortuneWhole()
    else:
        startFunctions()


# user can enter a part of the company's name, the search is case-insensitive
def fortuneOne():
    compName=input("Please enter the company's name which you are interested in: ").lower()
    count=0
    for k in range(0,100):
        if fortune_df.iloc[[k],[1]].values[0][0].lower().find(compName)!=-1:
            count+=1
            print ("This is how employees feel about their company:\n")
            compInfo = pd.DataFrame (fortune_df.iloc[[k], [0, 1, 3, 4, 5, 6, 7, 8]].values.T)[0]
            for i in compInfo:
                print (i)
            words = eval (fortune_df.iloc[[k], [2]].values[0][0])
            cloud_fortune = WordCloud ().generate_from_frequencies (words)
            plt.imshow (cloud_fortune, interpolation='bilinear')
            plt.title ("Why employees say this is a great place to work")
            plt.axis ("off")
            plt.show ()
    if count==0:
        print("We are so sorry, but the company that you are searching for is not in our system")
    back = input ("\nIf you want us to search that company online for you, please enter 1.\n"
                  "If you want to go back to Home Page, please enter 0: ")
    if (back == "0"):
        startFunctions ()
    elif back=="1":
        searchOnline()

#if the company is not in 100 FORTUNE Best List, search online information
'''Zhetian, Rahul, John'''
def searchOnline():
    return 0;


# # get link through selenium
# def getHTML(company, chromedriver_executable):
#     browser = webdriver.Chrome (executable_path=chromedriver_executable)
#     browser.get ("https://www.comparably.com")
#     search_bar = browser.find_element_by_xpath (
#         '/html/body/div/div/div[1]/div/div/div/div[1]/div/div/form/div/div/input')
#     search_bar.send_keys (company)
#     search_bar.send_keys (Keys.RETURN)
#     time.sleep (3)
#     browser.find_element_by_xpath ('/html/body/div/div/div/div/div[2]/div[1]/div/div[2]/a[1]/div/div/div[1]').click ()
#     return_this = (browser.current_url)
#     browser.close ()
#     return return_this
#
#
# # Getting reviews into a list
# def getReviews(html):
#     reviews = []
#     while html != '':
#         req = Request (html, headers={'User-Agent': 'Mozilla/5.0'})
#         comparably = BeautifulSoup (urlopen (req).read (), "lxml")
#         temp_reviews = comparably.find_all ('p', {"class": "cppRH-review-quote"})
#         for tag in temp_reviews:
#             if tag.find ('a') is None:
#                 reviews += tag.contents
#             else:
#                 reviews += tag.find ('a').contents
#         html = comparably.find_all ('a', {"class": "page"})[-1]['href']
#     return reviews
#
#     # Getting culture and ceo score
#     req = Request (html, headers={'User-Agent': 'Mozilla/5.0'})
#
#
# overview = BeautifulSoup (urlopen (req).read (), "lxml")
# try:
#     cultureDict[company] = overview.find ('div', {"class": "letterGrade"}).contents
#     ceoDict[company] = overview.find ('span', {"class": "grade-text"}).contents
# except:
#     cultureDict[company] = ['NA']
#     ceoDict[company] = ['-1']


#show the overall information of all the companies in
def fortuneWhole():
    #this shows the cloud for 100 companies
    words={}
    for j in range(100):
        newa = eval (fortune_df.iloc[[j], [2]].values[0][0])
        for key,value in newa.items():
            if key in words:
                words[key]+=value
            else:
                words[key]=value
    bg_pic=imageio.imread('100.jpg')
    cloud_fortune = WordCloud (mask=bg_pic,background_color='white',scale=3).generate_from_frequencies (words)
    plt.imshow (cloud_fortune, interpolation='bilinear')
    plt.title ("Why employees say these are great places to work")
    plt.axis ("off")
    plt.show ()
    #this shows some other features
    #scatter
    listx=[]
    y2,y3,y4,y5,y6=[],[],[],[],[]
    listy=[]
    for i in range(3,9):
        table=fortune_df.iloc[:, [i]].values
        for j in table:#get column 3,4,5,6,7,8's each(j) row
            if(i==3):listx.append(int(j[0][:2]))
            elif(i==4):y2.append(int(j[0][:2]))
            elif(i==5):y3.append(int(j[0][:2]))
            elif(i==6):y4.append(int(j[0][:2]))
            elif(i==7):y5.append(int(j[0][:2]))
            else:y6.append(int(j[0][:2]))
    for k in range(100):
        ave=(y2[k]+y3[k]+y4[k]+y5[k]+y6[k])/5
        listy.append(ave)
    data = {'x': listx,
            'y': listy,
            'color': np.random.randint (0, 101, 100),
            'size': np.arange(100,0,-1)} #higher-ranked companies have bigger size
    plt.scatter ('x', 'y', c='color', s='size', data=data)
    plt.xlabel ('% Employees say this is a great place to work')
    plt.ylabel ('% Employee experience satisfaction')
    plt.title ("Higher-ranked companies have bigger size")
    plt.show ()
    back = input ("\nIf you want to go back to Home Page, please enter 0: ")
    if (back == "0"):
        startFunctions ()







#This is where the program starts
print("WELCOME!")
print("JOBSCOPE: Ensuring you find the job meant for you!\n")
userID=input("Please enter your userID: ") #heinz
password=input("Please enter your password: ")#2019
if (userID=='heinz' and password=='2019'):
    startFunctions()
else:
    print("Sorry, wrong password.")
