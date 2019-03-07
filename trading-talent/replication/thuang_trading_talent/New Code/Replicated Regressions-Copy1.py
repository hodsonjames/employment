#!/usr/bin/env python
# coding: utf-8

# In[22]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
from sklearn import linear_model
from tqdm import tqdm


# In[23]:


column_names = ['Stock Symbol', 'YearMonth', 'NumEmployees', 'AverageAge', 'NumPeopleWithKnownAge', 'NumFemale', 'NumMale', 'NumNoSkills', 'Average Tenure', 'SkillsFreq']
month_current = pd.read_csv('fastwhitepaper_month_current.csv', sep="\t", error_bad_lines=False, names = column_names)
month_join = pd.read_csv('fastwhitepaper_month_join.csv', sep="\t", error_bad_lines=False, names = column_names)
month_leave = pd.read_csv('fastwhitepaper_month_leave.csv', sep="\t", error_bad_lines=False, names = column_names)


# In[24]:


month_current = month_current.rename(columns={'NumEmployees': 'NumEmployeesCurrent'})
month_join = month_join.rename(columns={'NumEmployees': 'NumEmployeesJoin'})
month_leave = month_leave.rename(columns={'NumEmployees': 'NumEmployeesLeave'})


# In[25]:


month_current_employees = month_current.iloc[:, 0:3]
month_join_employees = month_join.iloc[:, 2:3]
month_leave_employees = month_leave.iloc[:, 2:3]


# In[26]:


frames = [month_current_employees, month_join_employees, month_leave_employees]
month_combined = pd.concat(frames, axis=1, join='inner')
month_combined.head()


# In[27]:


num_employees_current = month_combined.loc[:,'NumEmployeesCurrent'].values.astype(float)
num_employees_join = month_combined.loc[:,'NumEmployeesJoin'].values.astype(float)
num_employees_leave = month_combined.loc[:,'NumEmployeesLeave'].values.astype(float)
join_depart_sum = np.add(num_employees_join, num_employees_leave)
turnover = np.divide(join_depart_sum, 
                     num_employees_current,
                     out=(np.zeros_like(join_depart_sum)),
                     where=(num_employees_current > 0))
turnover_df = pd.DataFrame(turnover, columns=['Turnover Rate'])


# In[28]:


frames = [month_combined, turnover_df]
month_combined_with_turnover = pd.concat(frames, axis=1, join='inner')
month_combined_with_turnover.head()


# In[29]:


minDate = min(month_combined_with_turnover.loc[:, 'YearMonth'])
maxDate = max(month_combined_with_turnover.loc[:, 'YearMonth'])
maxDate


# In[30]:


winsorized_turnover = scipy.stats.mstats.winsorize(month_combined_with_turnover["Turnover Rate"].values, limits=[0.01,0.01])
winsorized_turnover


# In[31]:


winsorized_turnover_df = pd.DataFrame(winsorized_turnover, columns=['Winsorized Turnover Rate'])


# In[32]:


frames = [month_combined, winsorized_turnover_df]
month_combined_with_winsorized_turnover = pd.concat(frames, axis=1, join='inner')
month_combined_with_winsorized_turnover.head()


# In[33]:


column_names = ['gvkey','datadate','fyearq','fqtr','indfmt','consol','popsrc','datafmt','tic','cusip','curcdq','datacqtr','datafqtr','rdq','ceqq','cshoq','epsf12','epsfxq','xrdq','costat','prccq','naics']
compustat_data = pd.read_csv('Compustat_2000_2016.csv', sep="\t", names = column_names)
compustat_data.head()


# In[34]:


report_date_df = pd.DataFrame(compustat_data['datadate'].values, columns=["Report Date"])
report_date_df.head()


# In[35]:


ticker = compustat_data['tic'].values
ticker_df = pd.DataFrame(ticker, columns=["Stock Symbol"])
frames = [report_date_df, ticker_df]
date_ticker_df = pd.concat(frames, axis=1, join='inner')
date_ticker_df.head()


# In[36]:


shares_outstanding = compustat_data['cshoq'].values
price_per_share = compustat_data['prccq'].values
market_capitalization = np.multiply(shares_outstanding, price_per_share)
size = np.log(market_capitalization)
size_df = pd.DataFrame(size, columns=["Size"])
frames = [report_date_df, size_df]
date_size_df = pd.concat(frames, axis=1, join='inner')
date_size_df.head()


# In[37]:


book_value = compustat_data['ceqq'].values
book_to_market_ratio = np.divide(book_value, market_capitalization, out=np.zeros_like(book_value), where=market_capitalization!=0)
book_to_market_ratio_df = pd.DataFrame(book_to_market_ratio, columns=["Book to Market Ratio"])
frames = [report_date_df, book_to_market_ratio_df]
date_book_to_market_ratio_df = pd.concat(frames, axis=1, join='inner')
date_book_to_market_ratio_df.head()


# In[38]:


def slicer_vectorized(a,start,end):
    b = a.view((str,1)).reshape(len(a),-1)[:,start:end]
    return np.fromstring(b.tostring(),dtype=(str,end-start))

naics_industry = compustat_data['naics'].values
naics_industry = slicer_vectorized(naics_industry.astype(str),0,2) #slicing naics by first 2 digits and storing as str

naics_industry_df = pd.DataFrame(naics_industry, columns=["NAICS Industry Classification"])
frames = [report_date_df, naics_industry_df]
date_naics_industry_df = pd.concat(frames, axis=1, join='inner')
date_naics_industry_df.head()


# In[39]:


# combined controls data
frames = [report_date_df, ticker_df, size_df, book_to_market_ratio_df, naics_industry_df]
combined_controls = pd.concat(frames, axis=1, join='inner')
combined_controls.head()


# In[40]:


len(month_combined_with_winsorized_turnover.loc[month_combined_with_winsorized_turnover['YearMonth'] > 200000])


# In[43]:


df1 = month_combined_with_winsorized_turnover
df2 = df1.loc[(df1['Stock Symbol'] == 'PM') & (df1['YearMonth'] == 201405)]
df2 = df2.append(df1.loc[(df1['Stock Symbol'] == 'MRK') & (df1['YearMonth'] == 200102)])
df2 = df2.append(df1.loc[(df1['Stock Symbol'] == 'C') & (df1['YearMonth'] == 200312)])
df2 = df2.append(df1.loc[(df1['Stock Symbol'] == 'JNJ') & (df1['YearMonth'] == 200805)])
df2 = df2.append(df1.loc[(df1['Stock Symbol'] == 'GOOG') & (df1['YearMonth'] == 201412)])
df2 = df2.append(df1.loc[(df1['Stock Symbol'] == 'APPL') & (df1['YearMonth'] == 200506)])
df2 = df2.append(df1.loc[(df1['Stock Symbol'] == 'IBM') & (df1['YearMonth'] == 201001)])
df2 = df2.append(df1.loc[(df1['Stock Symbol'] == 'GS') & (df1['YearMonth'] == 200708)])
df2 = df2.append(df1.loc[(df1['Stock Symbol'] == 'MCD') & (df1['YearMonth'] == 200212)])
df2 = df2.append(df1.loc[(df1['Stock Symbol'] == 'DAL') & (df1['YearMonth'] == 201105)])
df2


# In[48]:


df3 = combined_controls
df4 = df3.loc[(df3['Stock Symbol'] == 'PM') & (df3['Report Date'] // 100 <= 201405)]
df4 = df4.append(df3.loc[(df3['Stock Symbol'] == 'MRK') & (df3['Report Date'] // 100 <= 200102)])
df4 = df4.append(df3.loc[(df3['Stock Symbol'] == 'C') & (df3['Report Date'] // 100 <= 200312)])
df4 = df4.append(df3.loc[(df3['Stock Symbol'] == 'JNJ') & (df3['Report Date'] // 100 <= 200805)])
df4 = df4.append(df3.loc[(df3['Stock Symbol'] == 'GOOG') & (df3['Report Date'] // 100 <= 201412)])
df4 = df4.append(df3.loc[(df3['Stock Symbol'] == 'APPL') & (df3['Report Date'] // 100 <= 200506)])
df4 = df4.append(df3.loc[(df3['Stock Symbol'] == 'IBM') & (df3['Report Date'] // 100 <= 201001)])
df4 = df4.append(df3.loc[(df3['Stock Symbol'] == 'GS') & (df3['Report Date'] // 100 <= 200708)])
df4 = df4.append(df3.loc[(df3['Stock Symbol'] == 'MCD') & (df3['Report Date'] // 100 <= 200212)])
df4 = df4.append(df3.loc[(df3['Stock Symbol'] == 'DAL') & (df3['Report Date'] // 100 <= 201105)])


# In[49]:


# Function to match turnover data with most recent controls data
# Winsorized turnover dataframe has columns (Stock Symbol, YearMonth, NumEmployeesCurrent, 
# NumEmployeesJoin, NumEmployeesLeave, Winsorized Turnover Rate)
# Controls dataframe has columns (Report date, Stock Symbol, Size, Book to Market Ratio, 
# NAICS Industry Classification)

def match_func(wins_turnover_df, controls_df):
    matched_dict = dict()
    wins_turnover_df = wins_turnover_df.loc[wins_turnover_df['YearMonth'] >= 200000] # prune wins_turnover_df
    for index, row in tqdm(wins_turnover_df.iterrows()):
        nearest_row = None
        pruned_controls = controls_df.loc[(controls_df['Stock Symbol'] == row['Stock Symbol']) & (controls_df['Report Date'] // 100 <= row['YearMonth'])] #prune controls_df
        if (len(pruned_controls) > 0):
            nearest_index = pruned_controls['Report Date'].idxmax()
            nearest_row = pruned_controls.loc[nearest_index]
        matched_dict[(row['Stock Symbol'], row['YearMonth'], row['Winsorized Turnover Rate'])] = nearest_row
    return matched_dict


# In[51]:


matched_dict = match_func(df2, df4)


# In[56]:


matched_df = pd.DataFrame(matched_dict)
matched_df = matched_df.transpose()
matched_df.head(10)


# In[ ]:




