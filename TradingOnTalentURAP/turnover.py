import pandas as pd
import numpy as np
import math
from scipy.stats import mstats
from sklearn.linear_model import LinearRegression

# 1. Download data
current = pd.read_csv("/Users/jacquelinewood/Documents/TradingOnTalentURAP/fastwhitepaper_month_current.csv",sep='\t',header=None)
join = pd.read_csv("/Users/jacquelinewood/Documents/TradingOnTalentURAP/fastwhitepaper_month_join.csv",sep='\t',header=None)
leave = pd.read_csv("/Users/jacquelinewood/Documents/TradingOnTalentURAP/fastwhitepaper_month_leave.csv",sep='\t',header=None)

col_names = ['Stock Symbol','Year + Month','# Employees','Average Age','# People with Known Age','# Female','# Male','# with No Skills Listed','Average Tenure','Comma-separated Skills Frequencies']

current.columns = col_names
join.columns = col_names
leave.columns = col_names

current = current.loc[(current['Year + Month'] >= 200001)]
join = join.loc[(join['Year + Month'] >= 200001)]
leave = leave.loc[(leave['Year + Month'] >= 200001)]

# 2. Compute turnover variables from the three data files
# iterate over rows instead of calling data frames
turnover = current
turnover['Joined'] = join['# Employees']
turnover['Left'] = leave['# Employees']

def calc_turnover(row):
    new = row['Joined']
    depart = row['Left']
    n = row['# Employees']
    return (new + depart) / (n - new)

turn = []
for index, row in turnover.iterrows():
    try:
        turn.append(calc_turnover(row))
    except:
        turn.append(np.nan)

# 3. Winsorize turnover variable
turn = scipy.stats.mstats.winsorize(turn, limits=(.01,.01))
turnover['Turnover'] = turn

# 4. Compute size, book to market, industry and merge to turnover variables
dat = pd.read_csv("/Users/jacquelinewood/Documents/TradingOnTalentURAP/CRSP.csv") # monthly
dat['NAICS'] = [int(str(code)[:2]) if not np.isnan(code) else np.nan for code in dat['NAICS']]
dat['Year + Month'] = [int(str(date)[:-2]) for date in dat['date'].values]
dat['Market Value'] = dat['PRC'] * dat['SHROUT']
dat['Size'] = np.log(dat['Market Value'])

returns = dat[['PERMNO','date','TICKER','RET','sprtrn','Year + Month']]
dat = dat[['PERMNO','date','TICKER','NAICS','PRC','SHROUT','Year + Month','Market Value','Size']]

bookval = pd.read_csv("/Users/jacquelinewood/Documents/URAP/Compustat.csv")
bookval['Year + Month'] = [int(str(date)[:-2]) for date in bookval['datadate'].values]

merged = pd.merge(dat, bookval, how = 'outer', left_on = ['TICKER','Year + Month'], right_on = ['tic','Year + Month'])
merged = merged[['date','TICKER','NAICS','PRC','SHROUT','Year + Month','Market Value','Size','datafqtr','ceqq']]
sorted_merged = merged.sort_values(by = ['TICKER','date'])
frontfilled = sorted_merged[['datafqtr','ceqq']].fillna(method='ffill')
sorted_merged[['datafqtr','ceqq']] = frontfilled

# possibly keep book values in dictionary - BM seems to still be off

def calc_bmratio(row):
    book_val = row['ceqq']
    mkt_val = row['Market Value']
    return book_val / mkt_val

ratio = []
for index, row in sorted_merged.iterrows():
    try:
        ratio.append(calc_bmratio(row))
    except:
        ratio.append(np.nan)

sorted_merged['Book to Market Ratio'] = ratio

industry_dummy = pd.get_dummies(sorted_merged['NAICS'])

firm_chars = sorted_merged[['TICKER','Year + Month','Size','Book to Market Ratio']]
firm_chars = pd.concat([firm_chars,industry_dummy], axis=1)
firm_chars = pd.merge(firm_chars,turnover[['Stock Symbol','Year + Month','Turnover']],'inner',left_on=['TICKER','Year + Month'],right_on = ['Stock Symbol','Year + Month']).drop(['TICKER','Year + Month','Stock Symbol'], axis=1)
firm_chars = firm_chars.dropna()

# 5. Compute abnormal turnover : regress turnover on firm characteristics and take residuals
Y = firm_chars[['Turnover']]
X = firm_chars.drop(['Turnover'],axis=1)

reg = LinearRegression().fit(X, Y)
predictions = reg.predict(X)
abnormal_turnover = Y - predictions



# 6. Combine abnormal turnover with returns, using a lag (1 mo/2 mo/3 mo/6 mo)

returns = returns.sort_values(by = ['TICKER','date'])

def to_float(item):
    try:
        return float(item)
    except:
        return np.nan

returns['RET'] = [to_float(ret) for ret in returns['RET'].values]

returns['abnormal_return'] = returns['RET'] - returns['sprtrn']

Y = returns['RET']

def item(value):
    return value

grouped_returns = returns.groupby(['TICKER','Year + Month'])['RET','abnormal_return'].agg(item)

def shift_df(grouped,lag):
    shifted_dfs = []
    tickers = grouped.index.get_level_values('TICKER').unique()
    for ticker in tickers:
        shifted = grouped.loc[ticker].shift(lag)
        shifted['TICKER'] = np.repeat(ticker,len(shifted))
        shifted_dfs.append(shifted)
    lagged = pd.concat(shifted_dfs).reset_index().sort_values(by = ['TICKER','Year + Month'])
    lagged = lagged.rename(columns={"RET": "Lagged RET", "abnormal_return": "Lagged abnormal_return"})
    return lagged

lags = [1,2,3,6]

lagged = []
for L in lags:
    lagged.append(shift_df(grouped_returns,L))

Xs = []
Ys = []
for lag in lagged:
    merged = returns.merge(lag,on=['TICKER','Year + Month']).dropna()
    Xs.append(merged[['Lagged RET','Lagged abnormal_return']])
    Ys.append(merged[['RET']])

# Error here - will resolve ASAP
regs = []
for x_y in zip(Xs,Ys):
    reg = LinearRegression().fit(x_y[0], x_y[1])
    regs.append(reg)



