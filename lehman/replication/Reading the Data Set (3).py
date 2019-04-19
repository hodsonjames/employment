#!/usr/bin/env python
# coding: utf-8

# In[3]:


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


# In[4]:


#the columns names manually writen here from the taxonomy file since the csv files don't begin with a header
column_names = ["Username", "Name", "Birth Year", "Gender", "Skillset1", "Skillset1 Weight", "Skillset2", "Skillset2 Weight", "City","Country", "Education(highest degree attained)", "Elite Instituition", "Start Date", "???", "End Date", "???", "???", "Length", "Role", "Department", "Company Name", "Normalized Company Name", "Ticker", "Exchange", "Flag", "Location", "Industry", "Education Flag", "Degree Type", "Elite Flag", "Major", "Department(major category)", "FIGI", "Time Stamp"]       


# # Reading the Tab-delimited files into pandas's dataframe and the column names are specified.
# 
# 
# 

# In[167]:


LEH = pd.read_csv("LEH_profiles.csv", sep = '\t', header = None, names = column_names )


# In[168]:


DB = pd.read_csv("DB_profiles.csv", sep = '\t', header = None, names = column_names )


# In[169]:


GS = pd.read_csv("GS_profiles.csv", sep = '\t', header = None, names = column_names )


# In[170]:


MS = pd.read_csv("MS_profiles.csv", sep = '\t', header = None, names = column_names )


# In[171]:


UBS = pd.read_csv("UBS_profiles.csv", sep = '\t', header = None, names = column_names )


# In[172]:


# Identifying the number of rows in each dataset 
LEH.shape,DB.shape, UBS.shape, MS.shape,GS.shape


# # Preparing the dataset for analysis
# 

# In[5]:


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


# In[6]:


#retrieving of required columns
LT = required_columns(LEH).copy()
DB_Bank = required_columns(DB).copy()
GS_Bank = required_columns(GS).copy()
UBS_Bank = required_columns(UBS).copy()
MS_Bank = required_columns(MS).copy()


# In[175]:


#Conversion of time columns
lst = [LT, DB_Bank, GS_Bank,UBS_Bank,MS_Bank]
for i in lst:
    time_conversion(i)


# In[176]:


def updating_finance_industries(df):
    lst = list(Finance_updated_industry["Normalized Company Name"])
    for i in lst:
        df.loc[df["Normalized Company Name"] == i , "Industry"] = "52"
   


# In[78]:


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
    m = m.lower()
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


# In[60]:


#functions to check whether an employee works in the finance industry in 2016
def is_Finance(series):
    array = np.array(series)
    if 1 in array:
        return 1
    else:
        return 0
def finance_count(df):
    df = df.loc[:, ["Username", "Finance"]]
    username_grouped = df.groupby("Username").agg(is_Finance)
    finance = username_grouped.sum()[0]
    proportion = finance/ len(username_grouped.index)
    return proportion


# # Analysing the Lehman Employees

# In[179]:


#Filtered the lehman table to obtain the end date as of 2008/01/01 and company name is set to be lehman and obtained the list
#of id's of the employees.
#utiized the fill na method to fill the nan values with no company reported

Lst_of_ID = lst_2008(LT, "lehman")
Employees_ConsideredLEH = df_2016(LT, Lst_of_ID)


# In[282]:


#Employees_ConsideredLEH.loc[:, "Finance"] = Employees_ConsideredLEH["Industry"].apply(industry)
updating_finance_industries(Employees_ConsideredLEH)
Employees_ConsideredLEH.loc[:, "Finance"] = Employees_ConsideredLEH["Industry"].apply(industry)


# In[217]:


FinanceLH =Employees_ConsideredLEH.groupby("Finance").size()
FinanceLH


# In[218]:


finance_count(Employees_ConsideredLEH)


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

# In[181]:


Lst_of_IDB = lst_2008(DB_Bank,"deutsche")
Employees_consideredDB = df_2016(DB_Bank,Lst_of_IDB)


# In[283]:


updating_finance_industries(Employees_consideredDB)
Employees_consideredDB.loc[:, "Finance"] = Employees_consideredDB["Industry"].apply(industry)


# In[220]:



FinanceDB = Employees_consideredDB.groupby("Finance").size()
FinanceDB


# In[221]:


finance_count(Employees_consideredDB)
    


# # Analysis of GS bank

# In[222]:


# the GS table to obtain the end date as of 2008/01/01 and company name is set to be goldman sachs and obtained the list
#of id's of the employees.
Lst_of_IGS = lst_2008(GS_Bank, "goldman sachs")
Employees_consideredGS = df_2016(GS_Bank,Lst_of_IGS)


# In[284]:


updating_finance_industries(Employees_consideredGS)
Employees_consideredGS.loc[:, "Finance"] = Employees_consideredGS["Industry"].apply(industry)


# In[224]:


FinanceGS = Employees_consideredGS.groupby("Finance").size()
FinanceGS


# # Analysis of MS Bank

# In[183]:


# the MS table to obtain the end date as of 2008/01/01 and company name is set to be morgan stanley and obtained the list
#of id's of the employees.
Lst_of_IDMS = lst_2008(MS_Bank, "morgan stanley")
Employees_consideredMS = df_2016(MS_Bank, Lst_of_IDMS)


# In[285]:


updating_finance_industries(Employees_consideredMS)
Employees_consideredMS.loc[:, "Finance"] = Employees_consideredMS["Industry"].apply(industry)


# In[226]:


FinanceMS = Employees_consideredMS.groupby("Finance").size()
FinanceMS


# # Analysis of UBS Bank

# In[184]:


# the UBS table to obtain the end date as of 2008/01/01 and company name is set to be ubs and obtained the list
#of id's of the employees.
Lst_of_IDUBS = lst_2008(UBS_Bank, "ubs")
Employees_consideredUBS = df_2016(UBS_Bank, Lst_of_IDUBS)


# In[286]:


updating_finance_industries(Employees_consideredUBS)
Employees_consideredUBS.loc[:, "Finance"] = Employees_consideredUBS["Industry"].apply(industry)


# In[228]:



FinanceUBS = Employees_consideredUBS.groupby("Finance").size()
FinanceUBS


# # Analyzing the missing industry values

# In[312]:


#removing the rows with university in the ticker column
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


# In[313]:


#combining all the dataframes to produce a dataframe consisting of employees from all 5 bank
Combined_dataframe = pd.concat([leh,Db, Gs, Ubs, Ms], ignore_index = True)
Missing = missing_industries(Combined_dataframe)


# In[314]:


#exporting the dataframe to csv format
Missing.to_frame().to_csv(r'frequency.csv')


# In[315]:


freq = pd.read_csv('frequency.csv')
secondfreq = pd.read_csv('frequency.csv')
freq.head(2)


# In[316]:


freq["Industry"] = "None"
freq["Ticker"] = "None"
company_names = ["pwc", "ubs", "bank", "nomura","insurance", "julius baer","cfa", "mufg", "investec","icap",
                     "securities","wealth", "asset","raiffeisen schweiz","glencore","broadridge financial solutions",
                     "postfinance ag","brewin dolphin", "mizuho americas", "alliancebernstein", "s&p global","m&g investments",
                     "lord abbett & co llc","santander uk","mediobanca", "the depository trust & clearing corporation",
                 "fidelity worldwide investment", "rothschild & co", "ranieri partners management llc","partners group","partners group",
                "macquarie capital","lombard odier", "itaú bba", "bny mellon investment management","first reserve corporation","kpmg",
                "entrustpermal","metlife premier client group", "davidson companies","universität", "bnp", "goldman sachs",
                "blackrock", "barnum financial group", "citigroup", "citadel", "ci investments inc", "credit suisse", 
                 "credit-suisse", "standard chartered", "capital", "credit", "morgan stanley", "fs investments",
                "coutts & co", "six repo ag", "leste investimentos", "idb invest", "zais group", "jmp group",
                 "william blair & company", "winton group", "union bancaire privée", "agenda invest ag",
                 "litespeed management llc", "hft investment management", "iag new zealand", "zaisgroup", "j.p.morgan", "jp morgan", 
                "la caixa", "tudor pickering & holt", "barings", "the seaport group", "hq trust gmbh", "aib", 
                 "tilney group & bestinvest", "wells fargo", "tilney bestinvest group", "zekkou investments pte ltd", 
                "zodiac finance", "vanguard investments australia", "fbr & co", "fidelity", "finance", 
                 "infraenergy financial advisors", "dwl financial services llc", "e. gutzwiller & cie, banquiers",
                "global financial services", "global financial firm", "harbor investment advisory, llc", "hampden & co. plc", 
                "hamilton lane", "hamilton", "grameen koota financial services pvt. ltd.", "gpt group"]

university = ["hochschule für wirtschaft zürich hwz", "hochschule luzern", "fachhochschule nordwestschweiz fhnw",
                 "massachusetts institute of technology","harvard business school", "london business school",
                 "frankfurt school of finance & management", "universität st.gallen", "insead", "indian institute of management",
                 "imd business school","zhaw school of management and law","universität zürich", "universität bern", 
                  "zhaw zürcher hochschule für angewandte wissenschaften","columbia university","ucl", "eada business school",
                 "college for financial planning","berner fachhochschule bfh", "kalaidos fachhochschule schweiz", "university",
              "universitaria", "zhaw school of engineering","indian school of business", "harvard extension school",
             "business school", "hochschule", "college", "the london school of economics and political", 
              "london school of business and finance", "gordon institute of business science", "hec paris", "université", 
              "solvay brussels school","solvay brussels school", "kv zürich", "universitat", "ibw höhere fachschule südostschweiz",
             "le cordon bleu london", "hso wirtschaftsschule schweiz", "wiss - wirtschaftsinformatikschule schweiz", 
             "haute école de gestion arc", "harvard kennedy school", "stanford graduate school", 
              "erasmus universiteit rotterdam", "georgia institute of technology", "hhl leipzig graduate school of management",
              "harvard law school","hbu uster","trinity christian college", "lone star college" ]



for i in company_names:
    freq.loc[freq["Normalized Company Name"].str.contains(i), "Industry"] = 52
    freq.loc[freq["Normalized Company Name"].str.contains(i), "Ticker"] = "Finance"

for i in university:
    freq.loc[freq["Normalized Company Name"].str.contains(i), "Industry"] = "University"
    freq.loc[freq["Normalized Company Name"].str.contains(i), "Ticker"] = "University"


# In[317]:


Nonelist.shape


# In[318]:


Nonelist.iloc[850 : 900]


# In[319]:


Finance = freq[freq["Ticker"] == "Finance"]
Finance.to_csv(r'Finance')


# In[320]:


No_industry= freq[freq["Ticker"] == "None"]
Finance.to_csv(r'No_industry')


# In[321]:


University = freq[freq["Ticker"] == "University"]
#University.to_csv(r'Universities')


# In[322]:


University.head(2)


# In[215]:


Finance_updated_industry = freq[freq["Industry"] == 52]


# In[213]:


Finance_updated_industry.shape


# In[277]:


University.shape


# In[253]:


Industry_not_updated = freq[freq["Ticker"] == "None"]
Industry_not_updated.head(5)


# In[214]:


Industry_University = freq[freq["Ticker"] == "University"]
Industry_University.shape


# # Percentage of Employees in Finance

# In[232]:


Lehman_Percentage = finance_count(Employees_ConsideredLEH)
MS_Percentage = finance_count(Employees_consideredMS)
DB_Percentage = finance_count(Employees_consideredDB)
GS_Percentage = finance_count(Employees_consideredGS)
UBS_Percentage = finance_count(Employees_consideredUBS)
Lehman_Percentage, MS_Percentage, DB_Percentage, GS_Percentage, UBS_Percentage


# In[62]:


Lehman_Percentage


# In[233]:


x =np.array(["LEH", "MS", "DB", "GS", "UBS"])
y = np.array([Lehman_Percentage, MS_Percentage,DB_Percentage, GS_Percentage,UBS_Percentage,])*100
sns.set()
sns.barplot(x,y)
plt.xlabel("Type of Banks")
plt.ylabel("Percentage of Employees in Finance %")
plt.title("Percentage of Employees of the firms from 2008 who are working in finance in 2016");
plt.show()


# # Percentage of Time off

# In[234]:


Lehman_Percentage2 = FinanceLH[4]/ FinanceLH.sum()
MS_Percentage2 = FinanceMS[4]/ FinanceMS.sum()
DB_Percentage2 = FinanceDB[4]/ FinanceDB.sum()
GS_Percentage2 = FinanceGS[4]/ FinanceGS.sum()
UBS_Percentage2 = FinanceUBS[4]/ FinanceUBS.sum()
Lehman_Percentage2, MS_Percentage2, DB_Percentage2, GS_Percentage2, UBS_Percentage2


# In[235]:


x =np.array(["LEH", "MS", "DB", "GS", "UBS"])
y = np.array([Lehman_Percentage2, MS_Percentage2,DB_Percentage2, GS_Percentage2,UBS_Percentage2,])*100
sns.set()
sns.barplot(x,y)
plt.xlabel("Type of Banks")
plt.ylabel("Percentage of Employees who took time off")
plt.title("Percentage of Employees of the firms from 2008 as of 2016");
plt.show()


# # Switched Industries 

# In[303]:


def filter_finance(df):
    series = np.array(df["Industry"])
    for i in series:
        if "52" in i:
            return False
        else:
            return True

        
        
#Removing missing  values
def remove_nanindustry(df):
    #df = df[~(df["Industry"] == "nan")]
    df = df[~(df["Industry"] == "missing")]
    df = df[~(df["Industry"] == "time_off")]
    #df = df.loc[df["Ticker"]]
    return df

#the switched industries
def w_industry(m):
    if "61" in m:
        return "Education"
    elif "48" in m:
        return "Transportation"
    elif "54" in m:
        return "Scientific & Tech"
    elif "51" in m:
        return "Information"
    elif "53" in m:
        return "Real Estate"
    elif "33" in m:
        return "Manufacturing"
    elif m == "nan":
        return "unknown"
    else:
        return "other"
    
#only considering the employees who have switched from finance
Switched_financeLEH = Employees_ConsideredLEH.groupby("Username").filter(filter_finance)
Switched_financeDB  = Employees_consideredDB.groupby("Username").filter(filter_finance)
Switched_financeMS  = Employees_consideredMS.groupby("Username").filter(filter_finance)
Switched_financeUBS = Employees_consideredUBS.groupby("Username").filter(filter_finance)
Switched_financeGS  = Employees_consideredGS.groupby("Username").filter(filter_finance)

#adding a new column called switched
Switched_financeLEH.loc[:,"Firm"] = "LEH"
Switched_financeDB.loc[:,"Firm"] = "NonLEH"
Switched_financeMS.loc[:,"Firm"] = "NonLEH"
Switched_financeUBS.loc[:,"Firm"] = "NonLEH"
Switched_financeGS.loc[:,"Firm"] = "NonLEH"

#Producing final dataframe incorporating all the firm with employees switch from finance
Final_df = pd.concat([Switched_financeLEH,Switched_financeDB,Switched_financeMS,
                      Switched_financeUBS,Switched_financeGS], ignore_index = True)

#adding a new column called switched by investigating  to which industries these people switched to
Final_df.loc[:, "Switched"] = Final_df["Industry"].apply(w_industry)

#excluding the "other"
Final_df =Final_df[Final_df["Switched"] != "other"]


# In[305]:


sns.countplot(x="Switched", hue="Firm", data=Final_df);


# In[3]:


new_data = pd.read_csv("new_data_Lehman_cleaned.csv", sep = '\t', header )


# In[5]:


new_data.columns


# # Investigating the old dataset

# In[85]:


Column_names = ["Username", "Name", "Year of Birth", "Gender", "Ethnicity", "Primary Skill", "Primary Skill Weight", 
                "Secondary Skill", "Secondary Skil Weight", "Social Connectivity" , "City", 
               "Country", "Highest Education Achieved", "Elite Institution Flag", "Start Date", "End Date", "Duration (days)", 
              "Role Title", "Department", "Organization (as provided)", "Organization Official Name", "Organization Identifier", 
               "Exchange / Venue Traded", "Public Company Flag", "Location of Organization", "Industry", "Education Record Flagli", 
               "Education Record Level", "Education Record Elite Flag"]

new_data = pd.read_csv("new_data_Lehman_cleaned.csv", sep = ',', header = None, names = Column_names )


# In[86]:


new_data.shape


# In[87]:


new_data.rename({"Organization Identifier":"Normalized Company Name"}, inplace = True, axis = 1)
seriesE = new_data["End Date"].str.replace("None","0")
seriesS = new_data["Start Date"].str.replace("None", "0")
seriesE = seriesE.str.replace("-", "").astype(int)
seriesS = seriesS.str.replace("-", "").astype(int)
new_data.loc[:, "Normalized Company Name"] = new_data["Normalized Company Name"].str.lower()
new_data.loc[:,"End Date"] = seriesE
new_data.loc[:,"Start Date"] = seriesS
new_data = new_data[["Username", "Name", "Start Date", "End Date", "Normalized Company Name", "Industry"]]
time_2008 = ((new_data["End Date"]>= 20080101) & (new_data["Start Date"] <=20080101 ))
E_2008 = new_data[time_2008]
Leh_2008 =  E_2008[E_2008["Normalized Company Name"].str.contains("leh")]
Lst_leh08 = list(Leh_2008[~Leh_2008["Username"].duplicated()]["Username"])


# In[88]:


DB_2008 = E_2008[E_2008["Normalized Company Name"].str.contains("db")]
MS_2008 = E_2008[E_2008["Normalized Company Name"].str.contains("ms")]
GS_2008 = E_2008[E_2008["Normalized Company Name"].str.contains("gs")]
UBS_2008 = E_2008[E_2008["Normalized Company Name"].str.contains("ubs")]
Lst_DB08 = list(DB_2008[~DB_2008["Username"].duplicated()]["Username"])
Lst_MS08 = list(MS_2008[~MS_2008["Username"].duplicated()]["Username"])
Lst_GS08 = list(GS_2008[~GS_2008["Username"].duplicated()]["Username"])
Lst_UBS08 = list(UBS_2008[~UBS_2008["Username"].duplicated()]["Username"])


# In[89]:


LEH16 = df_2016(new_data, Lst_leh08)
DB16= df_2016(new_data, Lst_DB08)
MS16 = df_2016(new_data, Lst_MS08)
GS16 = df_2016(new_data, Lst_GS08)
UBS16 = df_2016(new_data, Lst_UBS08)


# In[90]:


LEH16.loc[:, "Finance"] = LEH16["Industry"].apply(industry)
DB16.loc[:, "Finance"] = DB16["Industry"].apply(industry)
MS16.loc[:, "Finance"] = MS16["Industry"].apply(industry)
GS16.loc[:, "Finance"] = GS16["Industry"].apply(industry)
UBS16.loc[:, "Finance"] = UBS16["Industry"].apply(industry)


# In[91]:


Lehman_Percentage = finance_count(LEH16)
MS_Percentage = finance_count(MS16)
DB_Percentage = finance_count(DB16)
GS_Percentage = finance_count(GS16)
UBS_Percentage = finance_count(UBS16)
Lehman_Percentage, MS_Percentage, DB_Percentage, GS_Percentage, UBS_Percentage


# In[92]:


x =np.array(["LEH", "MS", "DB", "GS", "UBS"])
y = np.array([Lehman_Percentage, MS_Percentage,DB_Percentage, GS_Percentage,UBS_Percentage,])*100
sns.set()
sns.barplot(x,y)
plt.xlabel("Type of Banks")
plt.ylabel("Percentage of Employees in Finance %")
plt.title("Percentage of Employees of the firms from 2008 who are working in finance in 2016");
plt.show()


# In[93]:


FinanceLH =LEH16.groupby("Finance").size()
FinanceDB =DB16.groupby("Finance").size()
FinanceMS =MS16.groupby("Finance").size()
FinanceGS =GS16.groupby("Finance").size()
FinanceUBS =UBS16.groupby("Finance").size()


# In[94]:


Lehman_Percentage2 = FinanceLH[4]/ FinanceLH.sum()
MS_Percentage2 = FinanceMS[4]/ FinanceMS.sum()
DB_Percentage2 = FinanceDB[4]/ FinanceDB.sum()
GS_Percentage2 = FinanceGS[4]/ FinanceGS.sum()
UBS_Percentage2 = FinanceUBS[4]/ FinanceUBS.sum()
Lehman_Percentage2, MS_Percentage2, DB_Percentage2, GS_Percentage2, UBS_Percentage2


# In[95]:


x =np.array(["LEH", "MS", "DB", "GS", "UBS"])
y = np.array([Lehman_Percentage2, MS_Percentage2,DB_Percentage2, GS_Percentage2,UBS_Percentage2,])*100
sns.set()
sns.barplot(x,y)
plt.xlabel("Type of Banks")
plt.ylabel("Percentage of Employees who took time off")
plt.title("Percentage of Employees of the firms from 2008 as of 2016");
plt.show()


# In[98]:


def filter_finance(df):
    series = np.array(df["Industry"])
    for i in series:
        if "52" in i:
            return False
        else:
            return True

        
        
#Removing missing  values
def remove_nanindustry(df):
    #df = df[~(df["Industry"] == "nan")]
    df = df[~(df["Industry"] == "missing")]
    df = df[~(df["Industry"] == "time_off")]
    #df = df.loc[df["Ticker"]]
    return df

#the switched industries
def w_industry(m):
    if "61" in m:
        return "Education"
    elif "48" in m:
        return "Transportation"
    elif "54" in m:
        return "Scientific & Tech"
    elif "51" in m:
        return "Information"
    elif "53" in m:
        return "Real Estate"
    elif "33" in m:
        return "Manufacturing"
    elif m == "nan":
        return "unknown"
    else:
        return "other"
    
#only considering the employees who have switched from finance
Switched_financeLEH = LEH16.groupby("Username").filter(filter_finance)
Switched_financeDB  = DB16.groupby("Username").filter(filter_finance)
Switched_financeMS  = MS16.groupby("Username").filter(filter_finance)
Switched_financeUBS = UBS16.groupby("Username").filter(filter_finance)
Switched_financeGS  = GS16.groupby("Username").filter(filter_finance)

#adding a new column called switched
Switched_financeLEH.loc[:,"Firm"] = "LEH"
Switched_financeDB.loc[:,"Firm"] = "NonLEH"
Switched_financeMS.loc[:,"Firm"] = "NonLEH"
Switched_financeUBS.loc[:,"Firm"] = "NonLEH"
Switched_financeGS.loc[:,"Firm"] = "NonLEH"

#Producing final dataframe incorporating all the firm with employees switch from finance
Final_df = pd.concat([Switched_financeLEH,Switched_financeDB,Switched_financeMS,
                      Switched_financeUBS,Switched_financeGS], ignore_index = True)

#adding a new column called switched by investigating  to which industries these people switched to
Final_df.loc[:, "Switched"] = Final_df["Industry"].apply(w_industry)

#excluding the "other"
Final_df =Final_df[Final_df["Switched"] != "other"]


# In[97]:


sns.countplot(x="Switched", hue="Firm", data=Final_df);


# In[ ]:





# In[ ]:




