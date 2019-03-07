#!/usr/bin/env python
# coding: utf-8

# In[43]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
from sklearn import linear_model
from tqdm import tqdm_notebook as tqdm


# In[44]:


column_names = ['Stock Symbol', 'YearMonth', 'NumEmployees', 'AverageAge', 'NumPeopleWithKnownAge', 'NumFemale', 'NumMale', 'NumNoSkills', 'Average Tenure', 'SkillsFreq']
month_current = pd.read_csv('fastwhitepaper_month_current.csv', sep="\t", error_bad_lines=False, names = column_names)
month_join = pd.read_csv('fastwhitepaper_month_join.csv', sep="\t", error_bad_lines=False, names = column_names)
month_leave = pd.read_csv('fastwhitepaper_month_leave.csv', sep="\t", error_bad_lines=False, names = column_names)


# In[45]:


month_current = month_current.rename(columns={'NumEmployees': 'NumEmployeesCurrent'})
month_join = month_join.rename(columns={'NumEmployees': 'NumEmployeesJoin'})
month_leave = month_leave.rename(columns={'NumEmployees': 'NumEmployeesLeave'})


# In[46]:


month_current_employees = month_current.iloc[:, 0:3]
month_join_employees = month_join.iloc[:, 2:3]
month_leave_employees = month_leave.iloc[:, 2:3]


# In[47]:


frames = [month_current_employees, month_join_employees, month_leave_employees]
month_combined = pd.concat(frames, axis=1, join='inner')
month_combined.head()


# In[48]:


num_employees_current = month_combined.loc[:,'NumEmployeesCurrent'].values.astype(float)
num_employees_join = month_combined.loc[:,'NumEmployeesJoin'].values.astype(float)
num_employees_leave = month_combined.loc[:,'NumEmployeesLeave'].values.astype(float)
join_depart_sum = np.add(num_employees_join, num_employees_leave)
turnover = np.divide(join_depart_sum, 
                     num_employees_current,
                     out=(np.zeros_like(join_depart_sum)),
                     where=(num_employees_current > 0))
turnover_df = pd.DataFrame(turnover, columns=['Turnover Rate'])


# In[49]:


frames = [month_combined, turnover_df]
month_combined_with_turnover = pd.concat(frames, axis=1, join='inner')
month_combined_with_turnover.head()


# In[50]:


minDate = min(month_combined_with_turnover.loc[:, 'YearMonth'])
maxDate = max(month_combined_with_turnover.loc[:, 'YearMonth'])
maxDate


# In[51]:


winsorized_turnover = scipy.stats.mstats.winsorize(month_combined_with_turnover["Turnover Rate"].values, limits=[0.01,0.01])
winsorized_turnover


# In[52]:


winsorized_turnover_df = pd.DataFrame(winsorized_turnover, columns=['Winsorized Turnover Rate'])


# In[53]:


frames = [month_combined, winsorized_turnover_df]
month_combined_with_winsorized_turnover = pd.concat(frames, axis=1, join='inner')
month_combined_with_winsorized_turnover.head()


# In[54]:


column_names = ['gvkey','datadate','fyearq','fqtr','indfmt','consol','popsrc','datafmt','tic','cusip','curcdq','datacqtr','datafqtr','rdq','ceqq','cshoq','epsf12','epsfxq','xrdq','costat','prccq','naics']
compustat_data = pd.read_csv('Compustat_2000_2016.csv', sep="\t", names = column_names)
compustat_data.head()


# In[55]:


report_date_df = pd.DataFrame(compustat_data['datadate'].values, columns=["Report Date"])
report_date_df.head()


# In[56]:


ticker = compustat_data['tic'].values
ticker_df = pd.DataFrame(ticker, columns=["Stock Symbol"])
frames = [report_date_df, ticker_df]
date_ticker_df = pd.concat(frames, axis=1, join='inner')
date_ticker_df.head()


# In[57]:


shares_outstanding = compustat_data['cshoq'].values
price_per_share = compustat_data['prccq'].values
market_capitalization = np.multiply(shares_outstanding, price_per_share)
size = np.log(market_capitalization)
size_df = pd.DataFrame(size, columns=["Size"])
frames = [report_date_df, size_df]
date_size_df = pd.concat(frames, axis=1, join='inner')
date_size_df.head()


# In[58]:


book_value = compustat_data['ceqq'].values
book_to_market_ratio = np.divide(book_value, market_capitalization, out=np.zeros_like(book_value), where=market_capitalization!=0)
book_to_market_ratio_df = pd.DataFrame(book_to_market_ratio, columns=["Book to Market Ratio"])
frames = [report_date_df, book_to_market_ratio_df]
date_book_to_market_ratio_df = pd.concat(frames, axis=1, join='inner')
date_book_to_market_ratio_df.head()


# In[59]:


def slicer_vectorized(a,start,end):
    b = a.view((str,1)).reshape(len(a),-1)[:,start:end]
    return np.fromstring(b.tostring(),dtype=(str,end-start))

naics_industry = compustat_data['naics'].values
naics_industry = slicer_vectorized(naics_industry.astype(str),0,2) #slicing naics by first 2 digits and storing as str

naics_industry_df = pd.DataFrame(naics_industry, columns=["NAICS Industry Classification"])
frames = [report_date_df, naics_industry_df]
date_naics_industry_df = pd.concat(frames, axis=1, join='inner')
date_naics_industry_df.head()


# In[60]:


# combined controls data
frames = [report_date_df, ticker_df, size_df, book_to_market_ratio_df, naics_industry_df]
combined_controls = pd.concat(frames, axis=1, join='inner')
combined_controls.head()


# In[62]:


# df1 = month_combined_with_winsorized_turnover
# row = df1.loc[(df1["Stock Symbol"] == 'PM') & (df1["YearMonth"] == 201405)]
# combined_controls = combined_controls.loc[(combined_controls['Stock Symbol'] == row.iloc[0]['Stock Symbol']) & (combined_controls['Report Date'] // 100 <= row.iloc[0]['YearMonth'])]
# nearest_index = combined_controls['Report Date'].idxmax()
# nearest_row = combined_controls.loc[nearest_index]
# nearest_row


# In[68]:


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


# In[ ]:


matched_dict = match_func(month_combined_with_winsorized_turnover, combined_controls)
matched_dict


# In[ ]:




