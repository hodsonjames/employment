#!/usr/bin/env python
# coding: utf-8

# In[1]:


#initializing the libraries required to read the data. I will be maintaining the same set of libariries throughout the project
import seaborn as sns
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import zipfile
from pathlib import Path
import datetime
# Default plot configurations
get_ipython().run_line_magic('matplotlib', 'inline')
plt.rcParams['figure.figsize'] = (16,8)
plt.rcParams['figure.dpi'] = 150
sns.set()


from IPython.display import display, Latex, Markdown


# In[2]:


#the columns names manually writen here from the taxonomy file since the csv files don't begin with a header
column_names = ["Username", "Name", "Birth Year", "Gender", "Skillset1", "Skillset1 Weight", "Skillset2", "Skillset2 Weight", "City","Country", "Education(highest degree attained)", "Elite Instituition", "Start Date", "???", "End Date", "???", "???", "Length", "Role", "Department", "Company Name", "Normalized Company Name", "Ticker", "Exchange", "Flag", "Location", "Industry", "Education Flag", "Degree Type", "Elite Flag", "Major", "Department(major category)", "FIGI", "Time Stamp"]       


# # Reading the Tab-delimited files into pandas's dataframe and the column names are specified.
# 
# 

# In[44]:


LEH = pd.read_csv("LEH_profiles.csv", sep = '\t', header = None, names = column_names )
LEH.head(5)


# In[45]:


DB = pd.read_csv("DB_profiles.csv", sep = '\t', header = None, names = column_names )
DB.head()


# In[46]:


GS = pd.read_csv("GS_profiles.csv", sep = '\t', header = None, names = column_names )
GS.head()


# In[47]:


MS = pd.read_csv("MS_profiles.csv", sep = '\t', header = None, names = column_names )
MS.head()


# In[48]:


UBS = pd.read_csv("UBS_profiles.csv", sep = '\t', header = None, names = column_names )
UBS.head()


# In[49]:


# Identifying the number of rows in each dataset 
LEH.shape,DB.shape, UBS.shape, MS.shape,GS.shape


# # Identifying the number of employees in each dataset
# 

# In[77]:


LEH["Username"].nunique()


# In[78]:


DB["Username"].nunique()


# In[79]:


UBS["Username"].nunique()


# In[80]:


MS["Username"].nunique()


# In[81]:


GS["Username"].nunique()


# # Studying the columns needed to build the propensity scoring !!!
# 1. Skill set
# 2. Gender 
# 3. Age 
# 4. Education
# 

# ## Learning about the skill set column
# 

# In[82]:


LEH["Skillset1"].dtype, UBS["Skillset1"].dtype, DB["Skillset1"].dtype, MS["Skillset1"].dtype, GS["Skillset1"].dtype


# In[83]:


LEH["Skillset1"].unique()


# In[84]:


UBS["Skillset1"].unique()


# In[85]:


DB["Skillset1"].unique()


# In[86]:


MS["Skillset1"].unique()


# In[87]:


GS["Skillset1"].unique()


# All the skill set1 columns are of string type and NAN value is seemed to be replaced with -1.
# 

# ## Gender
# 

# In[88]:


LEH["Gender"].dtype, UBS["Gender"].dtype, DB["Gender"].dtype, MS["Gender"].dtype, GS["Gender"].dtype


# In[89]:


LEH["Gender"].value_counts()


# In[90]:


LEH["Gender"].unique(), UBS["Gender"].unique(), DB["Gender"].unique(), MS["Gender"].unique(), GS["Gender"].unique()


# The data type is numerical(int). 1 corresponds to female, 2 corresponds to male and 0 correspond to unknown. The birth gender can be inferred from the namee of the employee.

# ## Age

# In[91]:


#the missing values are replaced by the None string
LEH["Birth Year"].unique()


# In[92]:


LEH[LEH["Birth Year"] == "None"]


# In[93]:


"None" in DB["Birth Year"].unique()


# In[94]:


DB[DB["Birth Year"] == "None"]["Birth Year"].value_counts()


# In[95]:


"None" in MS["Birth Year"].unique()


# In[96]:


"None" in UBS["Birth Year"].unique()


# In[97]:


"None" in GS["Birth Year"].unique()


# Based on my observation, the age for each employee as 2008 can be calculated by subtracting the birth year from 2008. The none rows are ignored.

# ## Education
# The educational level of an employee is studied through two aspects.
# 1. highest education -- highest degree attained
# 2. elite instituition

# In[98]:


LEH["Education(highest degree attained)"].unique(), LEH["Education(highest degree attained)"].dtype


# In[99]:


DB["Education(highest degree attained)"].unique(), DB["Education(highest degree attained)"].dtype


# In[100]:


UBS["Education(highest degree attained)"].unique(), UBS["Education(highest degree attained)"].dtype


# In[101]:


MS["Education(highest degree attained)"].unique(), MS["Education(highest degree attained)"].dtype


# In[102]:


GS["Education(highest degree attained)"].unique(), GS["Education(highest degree attained)"].dtype


# The Degree column is consistent witd description given and they are of int values.

# # Analysing LEHMAN employees

# In[9]:


#obtained the important columns from lehman table
LT = LEH[["Username", "Name", "Start Date", "End Date", "Company Name", "Industry"]]


# In[16]:


#Set the end date column to datetime object
#converted the company name to lowercase
LT.loc[:,"End Date"] = pd.to_datetime(LEH["End Date"], format = '%Y-%m-%d', errors = 'coerce')
LT.loc[:,"Start Date"] = pd.to_datetime(LEH["Start Date"], format = '%Y-%m-%d', errors = 'coerce')
LT.loc[:,"Company Name"] = LT["Company Name"].str.lower()


# In[17]:


#Filtered the lehman table to obtain the end date as of 2008/01/01 and company name is set to be lehman and obtained the list
#of id's of the employees.
#utiized the fill na method to fill the nan values with no company reported

Lehman_employees = LT[LT["Company Name"].fillna("No company reported").str.contains("lehman")].copy()
Lehman_employees.sort_values("End Date", ascending = True, inplace = True)
date_2008 = pd.Timestamp(2008, 1,1).date()

Lehman_time2 =  (Lehman_employees["End Date"].dt.date >= date_2008)
LH_2008 = Lehman_employees[Lehman_time2]
Lst_of_ID = list(LH_2008[~LH_2008["Username"].duplicated()]["Username"])


# In[18]:


# considered where the end date is greater than or equal to 2016-01-01
#only took the first row for each employee to note their industry as of 2016-01-01
m = pd.Timestamp(2016, 1, 1).date()
Filtered_based_on_datesLH = LT[ LT["End Date"].dt.date >= m]
Employees_consideredLH = Filtered_based_on_datesLH[Filtered_based_on_datesLH["Username"].isin(Lst_of_ID)]
Employeed_consideredLH = Employees_consideredLH[~Employees_consideredLH["Username"].duplicated()]


# In[19]:


# function to apply to find out the other the industry
def industry(m):
    if m == "nan" or m == "missing" or m == "time_off":
        return 3
    elif "52" in m:
        return 1
    
    else:
        return 2


# In[20]:


Employees_consideredLH.loc[:, "Industry"] = Employees_consideredLH["Industry"].astype(str).str.lower()
Employees_consideredLH.loc[:, "Finance"] = Employees_consideredLH["Industry"].apply(industry)


# In[22]:


FinanceLH = Employees_consideredLH.groupby("Finance").size()
FinanceLH


# # Analysis on DB Bank

# In[23]:


# Collecting the needed columns
# converting the datetime strings to datetime object
#converting all the company name to lower case
DB_Bank = DB[["Username", "Name", "Start Date", "End Date", "Company Name", "Industry"]].copy()
DB_Bank.loc[:,"End Date"] = pd.to_datetime(DB_Bank["End Date"], format = '%Y-%m-%d', errors = 'coerce')
DB_Bank.loc[:,"Start Date"] = pd.to_datetime(DB_Bank["Start Date"], format = '%Y-%m-%d', errors = 'coerce')
DB_Bank.loc[:,"Company Name"] = DB_Bank["Company Name"].str.lower()
DB_Bank.sort_values("End Date", ascending = True, inplace = True)
DB_Bank.head()


# In[24]:


#Filtered the DB table to obtain the end date as of 2008/01/01 and company name is set to be deutshe bank and obtained the list
#of id's of the employees.
#utiized the fill na method to fill the nan values with no company reported

DB_employees = DB_Bank[DB_Bank["Company Name"].fillna("No company reported").str.contains("deutsche bank")].copy()
date_2008 = pd.Timestamp(2008, 1,1).date()
DB_time2 =  (DB_employees["End Date"].dt.date >= date_2008)
DB_2008 = DB_employees[DB_time2]
Lst_of_IDDB = list(DB_2008[~DB_2008["Username"].duplicated()]["Username"])


# In[43]:


# considered where the end date is greater than or equal to 2016-01-01
#only took the first row for each employee to note their industry as of 2016-01-01
m = pd.Timestamp(2016, 1, 1).date()
Filtered_based_on_datesDB = DB_Bank[DB_Bank["End Date"].dt.date >= m]
Employees_consideredDB = Filtered_based_on_datesDB[Filtered_based_on_datesDB["Username"].isin(Lst_of_IDDB)]
Employeed_consideredDB = Employees_consideredDB[~Employees_consideredDB["Username"].duplicated()]
Employees_consideredDB.loc[:, "Industry"] = Employees_consideredDB["Industry"].astype(str).str.lower()
Employees_consideredDB.loc[:, "Finance"] = Employees_consideredDB["Industry"].apply(industry)


# In[26]:


FinanceDB = Employees_consideredDB.groupby("Finance").size()


# # Analysis of GS bank

# In[27]:


# Collecting the needed columns
# converting the datetime strings to datetime object
#converting all the company name to lower case
GS_Bank = GS[["Username", "Name", "Start Date", "End Date", "Company Name", "Industry"]].copy()
GS_Bank.loc[:,"End Date"] = pd.to_datetime(GS_Bank["End Date"], format = '%Y-%m-%d', errors = 'coerce')
GS_Bank.loc[:,"Start Date"] = pd.to_datetime(GS_Bank["Start Date"], format = '%Y-%m-%d', errors = 'coerce')
GS_Bank.loc[:,"Company Name"] = GS_Bank["Company Name"].str.lower()
GS_Bank.sort_values("End Date", ascending = True, inplace = True)
GS_Bank.head()


# In[28]:


# the GS table to obtain the end date as of 2008/01/01 and company name is set to be goldman sachs and obtained the list
#of id's of the employees.
#utiized the fill na method to fill the nan values with no company reported

GS_employees = GS_Bank[GS_Bank["Company Name"].fillna("No company reported").str.contains("goldman sachs")].copy()
date_2008 = pd.Timestamp(2008, 1,1).date()
GS_time2 =  (GS_employees["End Date"].dt.date >= date_2008)
GS_2008 = GS_employees[GS_time2]
Lst_of_IDGS = list(GS_2008[~GS_2008["Username"].duplicated()]["Username"])


# In[29]:


# considered where the end date is greater than or equal to 2016-01-01
#only took the first row for each employee to note their industry as of 2016-01-01
m = pd.Timestamp(2016, 1, 1).date()
Filtered_based_on_datesGS = GS_Bank[GS_Bank["End Date"].dt.date >= m]
Employees_consideredGS = Filtered_based_on_datesGS[Filtered_based_on_datesGS["Username"].isin(Lst_of_IDGS)]
Employeed_consideredGS = Employees_consideredGS[~Employees_consideredGS["Username"].duplicated()]
Employees_consideredGS.loc[:, "Industry"] = Employees_consideredGS["Industry"].astype(str).str.lower()
Employees_consideredGS.loc[:, "Finance"] = Employees_consideredGS["Industry"].apply(industry)


# In[30]:


FinanceGS = Employees_consideredGS.groupby("Finance").size()


# # Analysis of MS Bank

# In[31]:


# Collecting the needed columns
# converting the datetime strings to datetime object
#converting all the company name to lower case
MS_Bank = MS[["Username", "Name", "Start Date", "End Date", "Company Name", "Industry"]].copy()
MS_Bank.loc[:,"End Date"] = pd.to_datetime(MS_Bank["End Date"], format = '%Y-%m-%d', errors = 'coerce')
MS_Bank.loc[:,"Start Date"] = pd.to_datetime(MS_Bank["Start Date"], format = '%Y-%m-%d', errors = 'coerce')
MS_Bank.loc[:,"Company Name"] = MS_Bank["Company Name"].str.lower()
MS_Bank.sort_values("End Date", ascending = True, inplace = True)
MS_Bank.head()


# In[32]:


# the MS table to obtain the end date as of 2008/01/01 and company name is set to be morgan stanley and obtained the list
#of id's of the employees.
#utiized the fill na method to fill the nan values with no company reported

MS_employees =  MS_Bank[MS_Bank["Company Name"].fillna("No company reported").str.contains("morgan stanley")].copy()
date_2008 = pd.Timestamp(2008, 1,1).date()
MS_time2 =  (MS_employees["End Date"].dt.date >= date_2008)
MS_2008 = MS_employees[MS_time2]
Lst_of_IDMS = list(MS_2008[~MS_2008["Username"].duplicated()]["Username"])


# In[33]:


# considered where the end date is greater than or equal to 2016-01-01
#only took the first row for each employee to note their industry as of 2016-01-01
m = pd.Timestamp(2016, 1, 1).date()
Filtered_based_on_datesMS = MS_Bank[MS_Bank["End Date"].dt.date >= m]
Employees_consideredMS = Filtered_based_on_datesMS[Filtered_based_on_datesMS["Username"].isin(Lst_of_IDMS)]
Employeed_consideredMS = Employees_consideredMS[~Employees_consideredMS["Username"].duplicated()]
Employees_consideredMS.loc[:, "Industry"] = Employees_consideredMS["Industry"].astype(str).str.lower()
Employees_consideredMS.loc[:, "Finance"] = Employees_consideredMS["Industry"].apply(industry)


# In[34]:


FinanceMS = Employees_consideredMS.groupby("Finance").size()


# # Analysis of UBS Bank

# In[35]:


# Collecting the needed columns
# converting the datetime strings to datetime object
#converting all the company name to lower case
UBS_Bank = UBS[["Username", "Name", "Start Date", "End Date", "Company Name", "Industry"]].copy()
UBS_Bank.loc[:,"End Date"] = pd.to_datetime(UBS_Bank["End Date"], format = '%Y-%m-%d', errors = 'coerce')
UBS_Bank.loc[:,"Start Date"] = pd.to_datetime(UBS_Bank["Start Date"], format = '%Y-%m-%d', errors = 'coerce')
UBS_Bank.loc[:,"Company Name"] = UBS_Bank["Company Name"].str.lower()
#UBS_Bank.sort_values("End Date", ascending = True, inplace = True)
UBS_Bank.head()


# In[36]:


# the UBS table to obtain the end date as of 2008/01/01 and company name is set to be ubs and obtained the list
#of id's of the employees.
#utiized the fill na method to fill the nan values with no company reported

UBS_employees =  UBS_Bank[UBS_Bank["Company Name"].fillna("No company reported").str.contains("ubs")].copy()
date_2008 = pd.Timestamp(2008, 1,1).date()
UBS_time2 =  (UBS_employees["End Date"].dt.date >= date_2008)
UBS_2008 = UBS_employees[UBS_time2]
Lst_of_IDUBS = list(UBS_2008[~UBS_2008["Username"].duplicated()]["Username"])


# In[37]:


# considered where the end date is greater than or equal to 2016-01-01
#only took the first row for each employee to note their industry as of 2016-01-01
m = pd.Timestamp(2016, 1, 1).date()
Filtered_based_on_datesUBS = UBS_Bank[UBS_Bank["End Date"].dt.date >= m]
Employees_consideredUBS = Filtered_based_on_datesUBS[Filtered_based_on_datesUBS["Username"].isin(Lst_of_IDUBS)]
Employeed_consideredUBS = Employees_consideredUBS[~Employees_consideredUBS["Username"].duplicated()]
Employees_consideredUBS.loc[:, "Industry"] = Employees_consideredUBS["Industry"].astype(str).str.lower()
Employees_consideredUBS.loc[:, "Finance"] = Employees_consideredUBS["Industry"].apply(industry)


# In[38]:


FinanceUBS = Employees_consideredUBS.groupby("Finance").size()


# # Percentage of Employees in Finance

# In[42]:


Lehman_Percentage = FinanceLH[1]/ FinanceLH.sum()
MS_Percentage = FinanceMS[1]/ FinanceMS.sum()
DB_Percentage = FinanceDB[1]/ FinanceDB.sum()
GS_Percentage = FinanceGS[1]/ FinanceGS.sum()
UBS_Percentage = FinanceUBS[1]/ FinanceUBS.sum()
Lehman_Percentage, MS_Percentage, DB_Percentage, GS_Percentage, UBS_Percentage


# In[61]:


x =np.array(["LEH", "MS", "DB", "GS", "UBS"])
y = np.array([0.3600476687025175,0.4158825081347287,0.4273124124866156,0.41071625041258664,0.37691582174015564])*100
sns.set()
sns.barplot(x,y)
plt.xlabel("Type of Banks")
plt.ylabel("Percentage of Employees in Finance %")
plt.title("Percentage of Employees of the firms from 2008 who are working in finance in 2016");
plt.show()


# In[ ]:




