import pandas as pd
import numpy as np
import math
import scipy
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
def turnover(i,t):
    new = int(join.loc[(join['Year + Month'] == t) & (join['Stock Symbol'] == i)]['# Employees'])
    depart = int(leave.loc[(leave['Year + Month'] == t) & (leave['Stock Symbol'] == i)]['# Employees'])
    n = int(current.loc[(current['Year + Month'] == t) & (current['Stock Symbol'] == i)]['# Employees'])
    turnover = (new + depart) / n
    
    return turnover

# Is there a more efficient way to do this? Takes a very long time because current is large
# Should the turnover function be applied to current in the first place?  What (i,t) pairs should I pass in and from what data frame?
# From what dataset do I pull the firms and months to pass into the turnover function - current (fastwhitepaper_month_current) or dat (CRSP data)?
turn = []
for index, row in current.iterrows():
    try:
        turn.append(turnover(row['Stock Symbol'], row['Year + Month']))
    except:
        turn.append(np.nan)

# 3. Winsorize turnover variable
turn = scipy.stats.mstats.winsorize(turn, limits=(.01,.01))
current['Turnover'] = turn # Do I need to do this or instead just use it to make matrix for regression?

# 4. Compute size, book to market, industry and merge to turnover variables
dat = pd.read_csv("/Users/jacquelinewood/Documents/TradingOnTalentURAP/PriceVolIndustry.csv")
dat['Year + Month'] = [int(str(date)[:-2]) for date in dat['date'].values]
dat['Size'] = np.log(dat['PRC'] * dat['VOL'])

bkmkt = pd.read_csv("/Users/jacquelinewood/Documents/TradingOnTalentURAP/BookMkt.csv")
bkmkt['Calculated Market Value'] = bkmkt['prccq'] * bkmkt['cshoq']

# Know I am supposed to calculate the BMi,t, defined as firm i’s book-to-market ratio using book value from the most recent quarter-end preceding month t.
# How do I get the most recent quarter-end preceding month t  - bkmkt (from Compustat) only has a row per firm, per quarter, not by month?
# Do I have to merge with the larger dataset (dat from CRSP) in order to accurately calculate book value to use?
def calc_bm(quarter,firm):
    if quarter[-2:] == 'Q1':
        last_quarter = str(int(quarter[:4])-1) + 'Q4'
    else:
        last_quarter = quarter[:5] + str(int(quarter[-1:])-1)
    book_val = float(bkmkt.loc[(bkmkt['tic']==firm) & (bkmkt['datafqtr']==last_quarter)]['ceqq'])
    mkt_val = float(bkmkt.loc[(bkmkt['tic']==firm) & (bkmkt['datafqtr']==quarter)]['Calculated Market Value'])
    return book_val / mkt_val

ratio = []
for index, row in bkmkt.iterrows():
    try:
        ratio.append(calc_bm(row['datafqtr'], row['tic']))
    except:
        ratio.append(np.nan)

bkmkt['Book to Market Ratio'] = ratio #Just save this for vector of characteristics? But need to be able to merge them so need additional features.

combined = pd.merge(dat, bkmkt, how = 'outer', left_on = ['TICKER','date'], right_on = ['tic','datadate'])
combined = pd.merge(combined,current,how='outer',left_on = ['TICKER','Year + Month'],right_on = ['Stock Symbol','Year + Month'])
firm_chars = combined [['Size','Book to Market Ratio','HSICIG','Turnover']]

# 5. Compute abnormal turnover : regress turnover on firm characteristics and take residuals
X = firm_chars[['Size','Book to Market Ratio','HSICIG']]
Y = firm_chars[['Turnover']]

reg = LinearRegression().fit(X, Y)
predictions = reg.predict(X)
abnormal_turnover = Y - predictions



