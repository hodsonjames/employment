#!/usr/bin/env python
# coding: utf-8

# In[1]:


#initializing the libraries required to read the data. I will be maintaining the same set of libariries throughout the project
import seaborn as sns
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Default plot configurations
get_ipython().run_line_magic('matplotlib', 'inline')
plt.rcParams['figure.figsize'] = (16,8)
plt.rcParams['figure.dpi'] = 150
sns.set()


# In[2]:


#the columns names manually writen here from the taxonomy file since the csv files don't begin with a header
column_names = ["Username", "Name", "Birth Year", "Gender", "Skillset1", "Skillset1 Weight", "Skillset2", "Skillset2 Weight", "City","Country", "Education(highest degree attained)", "Elite Instituition", "Start Date", "???", "End Date", "???", "???", "Length", "Role", "Department", "Company Name", "Normalized Company Name", "Ticker", "Exchange", "Flag", "Location", "Industry", "Education Flag", "Degree Type", "Elite Flag", "Major", "Department(major category)", "FIGI", "Time Stamp"]       


# # Reading the Tab-delimited files into pandas's dataframe and the column names are specified.
# 
# 

# In[3]:


LEH = pd.read_csv("LEH_profiles.csv", sep = '\t', header = None, names = column_names )


# In[4]:


DB = pd.read_csv("DB_profiles.csv", sep = '\t', header = None, names = column_names )


# In[5]:


GS = pd.read_csv("GS_profiles.csv", sep = '\t', header = None, names = column_names )


# In[6]:


MS = pd.read_csv("MS_profiles.csv", sep = '\t', header = None, names = column_names )


# In[7]:


UBS = pd.read_csv("UBS_profiles.csv", sep = '\t', header = None, names = column_names )


# In[8]:


# Identifying the number of rows in each dataset 
LEH.shape,DB.shape, UBS.shape, MS.shape,GS.shape


# # Preparing the dataset for analysis
# 

# In[9]:


#to convert the time string to integers
def time_conversion(df):
    df.loc[df["End Date"] == "None","End Date"] = "00000000"
    df.loc[df["Start Date"] == "None", "Start Date"] = "00000000"
    seriesE = df["End Date"].str.replace("-","").astype(int)
    seriesS = df["Start Date"].str.replace("-","").astype(int)
    df.loc[:,"End Date"] = seriesE
    df.loc[:,"Start Date"] = seriesS
#to derive required columns    
def required_columns(Dataframe):
    columns = ["Username", "Name", "Start Date", "End Date", "Normalized Company Name", "Industry",'Ticker']
    return Dataframe[columns]


# In[10]:


#retrieving of required columns
LT = required_columns(LEH).copy()
DB_Bank = required_columns(DB).copy()
GS_Bank = required_columns(GS).copy()
UBS_Bank = required_columns(UBS).copy()
MS_Bank = required_columns(MS).copy()


# In[11]:


#Conversion of time columns
lst = [LT, DB_Bank, GS_Bank,UBS_Bank,MS_Bank]
for i in lst:
    time_conversion(i)


# In[14]:


LT["Normalized Company Name"]


# In[15]:


#to output the list of employees as of 2008
#utiized the fill na method to fill the nan values with no company reported
def lst_2008(df, company_name):
    df.fillna(value= {"Normalized Company Name": "No Company"}, inplace = True)
    df.loc[:, "Normalized Company Name"] = df["Normalized Company Name"].astype(str)
    df.loc[:, "Normalized Company Name"] = df["Normalized Company Name"].str.lower()
    df.loc[:, 'Industry'] = df["Industry"].astype(str)
    df.loc[:, 'Industry'] = df["Industry"].str.lower()
    employees =  df[df["Normalized Company Name"].str.contains(company_name)]
    time_2008 = ((employees["End Date"]>= 20080101) & (employees["Start Date"] <=20080101 ))
    E_2008 = employees[time_2008]
    Lst_of_ID = list(E_2008[~E_2008["Username"].duplicated()]["Username"])
    return Lst_of_ID

#to output a dataframe consisting the employees of Lehman in 2008 as of 2016
# considered where the end date is greater than or equal to 2016-01-01
#only took the first row for each employee to note their industry as of 2016-01-01
def df_2016(df, lstID):
    mask_2016 =(df["End Date"] >= 20160101) & (df["Start Date"] <= 20160101)
    filtered = df[mask_2016]
    employees = filtered[filtered["Username"].isin(lstID)]
    employees.loc[:, "Industry"] = employees["Industry"].astype(str)
    employees.loc[:, "Industry"] = employees["Industry"].str.lower()
    return employees

# function to apply to find out the other the industry
def industry(m):
    if m == "nan" :
        return 3
    elif m == "time_off" or m == "missing":
        return 4
    elif "52" in m:
        return 1
    
    else:
        return 2
    
#produces a series contaning the companies and the corresponding number of missing values in the industry column
def missing_industries(df):
    df2 = df[df["Industry"].isin(["missing", "nan"])]
    return df2.groupby("Normalized Company Name").size().sort_values(ascending = False)

#resetting the industry for known firms
def industryreplacement(df):
    keywords = ["pwc","zais", "mint partners", "capital", "bank", "securities", "nomura", "investec", 
"trading", "goldman", "insurance", "wealth","barclays", "asset management", "credit suisse", "funds", "equity",
"ventures", "wake usa llc", "volkswagen credit", "funds management", "mufg", "banking", "moody's", "mizuho"
"credit card","zais financial corp", "wells fargo" ]
    for i in keywords:
        mask = (df["Company Name"].str.contains(i)) & ((df["Industry"] == "nan") | (df["Industry"] == "missing"))
        df.loc[mask , "Industry"] = "52"

        


# In[ ]:





# In[ ]:


.loc[LT["Industry"].str.contains("time_off"),:]["Company Name"].unique()


# # Analysing the Lehman Employees

# In[16]:


#Filtered the lehman table to obtain the end date as of 2008/01/01 and company name is set to be lehman and obtained the list
#of id's of the employees.
#utiized the fill na method to fill the nan values with no company reported

Lst_of_ID = lst_2008(LT, "lehman")
Employees_ConsideredLEH = df_2016(LT, Lst_of_ID)


# In[17]:


Employees_ConsideredLEH.loc[:, "Finance"] = Employees_ConsideredLEH["Industry"].apply(industry)


# In[18]:


FinanceLH =Employees_ConsideredLEH.groupby("Finance").size()
FinanceLH


# nomura securities ,nomura international pwc ,nomura international plc ,mufg securities
# iag new zealand
# banyan point, llc
# beka finance
# advance corporate finance
# aalto invest llp
# ar global
# apollo global management llc-- asset management
# dlj real estate capital partners
# bt pension scheme
# cinnober financial technology north
# teksystems at bank of america
# shapoorji pallonji investment advisors
# srf ventures
# w.j. bradley company
# morgan stanley advantage services
# mitsubishi ufj trust and banking corporation
# miscellaneous ventures
# quvat management pte ltd
# rothschild & co

# # Analysis on DB Bank

# In[21]:


Lst_of_IDB = lst_2008(DB_Bank,"deutsche")
Employees_consideredDB = df_2016(DB_Bank,Lst_of_IDB)


# In[22]:



Employees_consideredDB.loc[:, "Finance"] = Employees_consideredDB["Industry"].apply(industry)


# In[23]:


FinanceDB = Employees_consideredDB.groupby("Finance").size()
FinanceDB


# # Analysis of GS bank

# In[24]:


# the GS table to obtain the end date as of 2008/01/01 and company name is set to be goldman sachs and obtained the list
#of id's of the employees.
Lst_of_IGS = lst_2008(GS_Bank, "goldman sachs")
Employees_consideredGS = df_2016(GS_Bank,Lst_of_IGS)


# In[25]:



Employees_consideredGS.loc[:, "Finance"] = Employees_consideredGS["Industry"].apply(industry)


# In[26]:


FinanceGS = Employees_consideredGS.groupby("Finance").size()
FinanceGS


# In[ ]:





# # Analysis of MS Bank

# In[27]:


# the MS table to obtain the end date as of 2008/01/01 and company name is set to be morgan stanley and obtained the list
#of id's of the employees.
Lst_of_IDMS = lst_2008(MS_Bank, "morgan stanley")
Employees_consideredMS = df_2016(MS_Bank, Lst_of_IDMS)


# In[28]:



Employees_consideredMS.loc[:, "Finance"] = Employees_consideredMS["Industry"].apply(industry)


# In[29]:


FinanceMS = Employees_consideredMS.groupby("Finance").size()
FinanceMS


# # Analysis of UBS Bank

# In[30]:


# the UBS table to obtain the end date as of 2008/01/01 and company name is set to be ubs and obtained the list
#of id's of the employees.
Lst_of_IDUBS = lst_2008(UBS_Bank, "ubs")
Employees_consideredUBS = df_2016(UBS_Bank, Lst_of_IDUBS)


# In[31]:


Employees_consideredUBS.loc[:, "Finance"] = Employees_consideredUBS["Industry"].apply(industry)


# In[32]:


FinanceUBS = Employees_consideredUBS.groupby("Finance").size()
FinanceUBS


# # Analyzing the missing industry values

# In[33]:


#removing the rows with university in the ticker row
def university_remover(data):
    df = data.copy()
    df['Ticker'] = df['Ticker'].str.lower()
    df= df.loc[df['Ticker'] != 'university',:]
    return df
#gathering information regarding the employees with missing values as 0f 2016
leh = university_remover(Employees_ConsideredLEH)
Db =  university_remover(Employees_consideredDB)
Gs =  university_remover(Employees_consideredGS)
Ubs =  university_remover(Employees_consideredUBS)
Ms =  university_remover(Employees_consideredMS)    


# In[34]:


#combining all the dataframes to produce a dataframe consisting of employees from all 5 bank
Combined_dataframe = pd.concat([leh,Db, Gs, Ubs, Ms], ignore_index = True)
Missing = missing_industries(Combined_dataframe)
Missing.index[0:32]


# In[35]:


#exporting the dataframe to csv format
Missing.to_frame().to_csv(r'frequency.csv')


# In[36]:


pd.read_csv('frequency.csv')


# # Percentage of Employees in Finance

# In[37]:


Lehman_Percentage = FinanceLH[1]/ FinanceLH.sum()
MS_Percentage = FinanceMS[1]/ FinanceMS.sum()
DB_Percentage = FinanceDB[1]/ FinanceDB.sum()
GS_Percentage = FinanceGS[1]/ FinanceGS.sum()
UBS_Percentage = FinanceUBS[1]/ FinanceUBS.sum()
Lehman_Percentage, MS_Percentage, DB_Percentage, GS_Percentage, UBS_Percentage


# In[39]:


x =np.array(["LEH", "MS", "DB", "GS", "UBS"])
y = np.array([Lehman_Percentage, MS_Percentage,DB_Percentage, GS_Percentage,UBS_Percentage,])*100
sns.set()
sns.barplot(x,y)
plt.xlabel("Type of Banks")
plt.ylabel("Percentage of Employees in Finance %")
plt.title("Percentage of Employees of the firms from 2008 who are working in finance in 2016");
plt.show()


# # Percentage of Time off

# In[40]:


Lehman_Percentage2 = FinanceLH[4]/ FinanceLH.sum()
MS_Percentage2 = FinanceMS[4]/ FinanceMS.sum()
DB_Percentage2 = FinanceDB[4]/ FinanceDB.sum()
GS_Percentage2 = FinanceGS[4]/ FinanceGS.sum()
UBS_Percentage2 = FinanceUBS[4]/ FinanceUBS.sum()
Lehman_Percentage2, MS_Percentage2, DB_Percentage2, GS_Percentage2, UBS_Percentage2


# In[41]:


x =np.array(["LEH", "MS", "DB", "GS", "UBS"])
y = np.array([Lehman_Percentage2, MS_Percentage2,DB_Percentage2, GS_Percentage2,UBS_Percentage2,])*100
sns.set()
sns.barplot(x,y)
plt.xlabel("Type of Banks")
plt.ylabel("Percentage of Employees who took time off")
plt.title("Percentage of Employees of the firms from 2008 as of 2016");
plt.show()


# In[ ]:


#Considering only the employees who a

