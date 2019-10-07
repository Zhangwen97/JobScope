from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import imageio
import Indeed
import glassdoor_scrape_online
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
    global compName
    compName=input("Please enter the company's name which you are interested in: ").lower()
    count=0
    for k in range(0,100):
        if fortune_df.iloc[[k],[1]].values[0][0].lower().find(compName)!=-1:
            count+=1
            #show data for one company
            print ("This is how employees feel about their company:\n")
            compInfo = pd.DataFrame (fortune_df.iloc[[k], [0, 1, 3, 4, 5, 6, 7, 8]].values.T)[0]
            compInfo2 = pd.DataFrame (fortune_df.iloc[[k], [9,10,11,12,13,14]].values.T)[0]
            compInfo3 = pd.DataFrame (fortune_df.iloc[[k], [16,17]].values.T)[0]

            print("Information from: Great place to Work")
            for i in compInfo:
                print (i)#
            print()
            print("Information from: Glassdoor")
            for j in range(6):
                if j==0: print("Overall Stars: ",compInfo2[j])
                elif j==1: print("Culture & Values: ",compInfo2[j])
                elif j==2:print("Work/Life Balance: ",compInfo2[j])
                elif j==3:print("Senior Management: ",compInfo2[j])
                elif j == 4:print ("Compensation & Benefits: ", compInfo2[j])
                elif j==5:print("Career Opportunities: ",compInfo2[j])
            print()
            print("Information from: Comparably")
            for n in range(2):
                if n==0:print("culture_score: ",compInfo2[n])
                elif n==1:print("ceo_score: ",compInfo2[n])
            #wordcloud for one company
            words = eval (fortune_df.iloc[[k], [2]].values[0][0])
            bg_pic = imageio.imread ('one.png')
            cloud_fortune = WordCloud (mask=bg_pic, background_color='white', scale=3).generate_from_frequencies (words)
            plt.imshow (cloud_fortune, interpolation='bilinear')
            plt.title ("Why employees say this is a great place to work")
            plt.axis ("off")
            plt.show ()
    Indeed.indeed (compName.capitalize ())
    if count==0:
        print("We are so sorry, but we don't have much information about this company")
        print("If you want us to search that company online for you, please enter 1.")
    back = input ("If you want to go back to Home Page, please enter 0: ")
    if (back == "0"):
        startFunctions ()
    elif back=="1":
        searchOnline(compName)
        review_file_name = "Indeed_review.csv"
        rate_file_name = "Indeed_rate.csv"
        try:
            Indeed.search_url(compName)
            company_rates = Indeed.get_rate(compName.capitalize())
            company_rates.to_csv(rate_file_name, mode='a', header=False)
            value = list (company_rates.iloc[0, 0:5])
            Indeed.show_radar(compName, value)

            company = Indeed.main(compName)
            Indeed.show_trend(company[company['company'] == compName], compName)
            company.to_csv (review_file_name, mode='a', header=False)
        except Exception as e:
            print(e)
            print("Sorry we couldn't find the data from Indeed.")

#if the company is not in 100 FORTUNE Best List, search online information
'''Zhetian, Rahul, John'''
def searchOnline(compName):
    chromedriver_executable = 'chromedriver'
    glassdoor_scrape_online.find_company_glassdoor(compName, chromedriver_executable)
    comparably_word_freq = glassdoor_scrape_online.getComparablyInfoSingleCompany(compName,chromedriver_executable)
    bg_pic = imageio.imread ('one.png')
    cloud_fortune = WordCloud (mask=bg_pic, background_color='white', scale=3).generate_from_frequencies (comparably_word_freq)
    plt.imshow (cloud_fortune, interpolation='bilinear')
    plt.title ("Why employees say this is a great place to work")
    plt.axis ("off")
    plt.show ()




#show the overall information of all the companies in
def fortuneWhole():
    # cloud
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
    # scatter
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






if __name__ == '__main__':
    #This is where the program starts
    print("WELCOME!")
    print("JOBSCOPE: Ensuring you find the job meant for you!\n")
    userID=input("Please enter your userID: ") #heinz
    # import getpass
    # password = getpass.getpass("fdf")
    password=input("Please enter your password: ")#2019
    if (userID=='heinz' and password=='2019'):
        startFunctions()
    else:
        print("Sorry, wrong password.")


