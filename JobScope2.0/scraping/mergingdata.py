import pandas as pd

greatplace=pd.read_csv('greatplace.csv')
comscore=pd.read_csv('comparably_scores_all.csv')
comreviews=pd.read_csv('reviews_word_freq.csv')
glassscores=pd.read_csv('glassdoor_data.csv')

greatplace_df=pd.DataFrame (greatplace)
comscore_df=pd.DataFrame (comscore)#100 in sequence: second
comreviews_df=pd.DataFrame(comreviews)#80? in sequence: some missing:
glassscores_df=pd.DataFrame(glassscores)#100 in sequence :first

dfa=pd.merge(greatplace_df,glassscores_df,how='outer',left_on='company',right_on='Company Name')
dfb=pd.merge(dfa,comscore_df,how='outer',left_on='company',right_on='Unnamed: 0')
dfc=pd.merge(dfb,comreviews_df,how='outer',left_on='company',right_on='0')
del dfc['0']

dfc=dfc.fillna("{}")
list1_2 = []
for j in range (100):
    dict1 = eval (dfc.iloc[[j], [2]].values[0][0])
    dict2 = eval (dfc.iloc[[j], [21]].values[0][0])
    for key, value in dict1.items ():
        if key.strip() in dict2:
            dict2[key.strip()] += value
        else:
            dict2[key.strip()] = value
    list1_2.append(str(dict2))

dfc['impressions_for_wordcloud']=list1_2

del dfc['Company Name']
del dfc['Unnamed: 0_y']
del dfc['Unnamed: 0_x']
dfc.insert(0,'Unnamed: 0',range(1,101))
dfc=dfc.set_index('Unnamed: 0')
dfc.to_csv ('fortune100.csv')

