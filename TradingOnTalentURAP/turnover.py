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
turn = mstats.winsorize(turn, limits=(.01,.01))
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
bookval['ceqq'] = bookval['ceqq'] * 1000 #said it was in millions but this is what makes it equal intermediate values?
bookval['Year + Month'] = [int(str(date)[:-2]) for date in bookval['datadate'].values]

bookval.loc[bookval['tic'] == 'GOOGL', 'tic'] = 'GOOG'

merged = pd.merge(dat, bookval, how = 'outer', left_on = ['TICKER','Year + Month'], right_on = ['tic','Year + Month'])
merged = merged.sort_values(by = ['TICKER','date'])

# BMR

def item(value):
    return value

quarters = merged.groupby(['TICKER','Year + Month'])['datafqtr','ceqq'].agg(item)

quarts = []
ticks = quarters.index.get_level_values('TICKER').unique()
for tic in ticks:
    quart = quarters.loc[tic]
    begin_mos = quart.loc[quart['ceqq'] > 0 ].index.values
    quart['TICKER'] = np.repeat(tic,len(quart))
    frontfill = quart[['datafqtr','ceqq']].fillna(method='ffill')
    quart[['datafqtr','ceqq']] = frontfill
    
    #addition
    for mo in begin_mos:
        quart  = quart.set_value(mo, 'ceqq', np.nan)
    frontfill_ceqqs = quart[['ceqq']].fillna(method='ffill')
    quart[['ceqq']] = frontfill_ceqqs

    backfill_ceqqs = quart[['ceqq']].fillna(method='bfill')
    quart[['ceqq']] = backfill_ceqqs
    
    
    quarts.append(quart)
back = pd.concat(quarts).reset_index().sort_values(by = ['TICKER','Year + Month'])
merged = pd.merge(merged,back,on=['TICKER','Year + Month']).drop(['datafqtr_x','ceqq_x'], axis=1).rename(columns={'datafqtr_y': 'datafqtr','ceqq_y':'ceqq'})

# how to handle something with no previous (like 200001) - just keep value?

sorted_merged = merged.sort_values(by = ['TICKER','date'])

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

def to_float(val):
    try:
        return float(val)
    except:
        return np.nan

sorted_merged['Book to Market Ratio'] = [to_float(bmr) for bmr in sorted_merged['Book to Market Ratio'].values]

grouped_industries = sorted_merged.groupby(['TICKER'])['NAICS'].apply(max)

industries = dict(grouped_industries)
ind = []
for index, row in sorted_merged.iterrows():
    try:
        ind.append(industries[row['TICKER']])
    except:
        ind.append(np.nan)
sorted_merged['NAICS'] = ind

industry_dummy = pd.get_dummies(sorted_merged['NAICS'])

firm_chars = pd.concat([sorted_merged[['TICKER','Year + Month','Size','Book to Market Ratio']],industry_dummy], axis=1)
firm_chars = pd.merge(firm_chars,turnover[['Stock Symbol','Year + Month','Turnover']],'inner',left_on=['TICKER','Year + Month'],right_on = ['Stock Symbol','Year + Month']).drop(['Stock Symbol'], axis=1)
firm_chars = firm_chars.dropna()

# 5. Compute abnormal turnover : regress turnover on firm characteristics and take residuals
Y = firm_chars[['Turnover']]
X = firm_chars.drop(['Turnover','TICKER','Year + Month'],axis=1)

reg = LinearRegression().fit(X, Y)
predictions = reg.predict(X)
abnormal_turnover = Y - predictions

firm_chars['abnormal_turnover'] = abnormal_turnover
sorted_merged = pd.merge(sorted_merged, firm_chars[['TICKER','Year + Month','abnormal_turnover']], how='outer', on=['TICKER','Year + Month'])

# 6. Combine abnormal turnover with returns, using a lag (1 mo/2 mo/3 mo/6 mo)

returns = returns.sort_values(by = ['TICKER','date'])

returns['RET'] = [to_float(ret) for ret in returns['RET'].values]

returns['abnormal_return'] = returns['RET'] - returns['sprtrn']

total = pd.merge(sorted_merged,turnover,left_on=['TICKER','Year + Month'],right_on = ['Stock Symbol','Year + Month'])
total = pd.merge(total,returns, on = ['TICKER','Year + Month','date'])

def item(value):
    return value

def shift_df(total,lag,x_column):
    grouped = pd.DataFrame(total.groupby(['TICKER','Year + Month'])[x_column].agg(item))
    shifted_dfs = []
    tickers = grouped.index.get_level_values('TICKER').unique()
    for ticker in tickers:
        shifted = grouped.loc[ticker].shift(lag)
        shifted['TICKER'] = np.repeat(ticker,len(shifted))
        shifted_dfs.append(shifted)
    lagged = pd.concat(shifted_dfs).reset_index().sort_values(by = ['TICKER','Year + Month'])
    lagged = lagged.rename(columns={x_column: "Lagged " + x_column})
    return lagged

def run_return_regressions(total,x_var,y_var):
    lags = [1,2,3,6]
    lagged = []
    for L in lags:
        lagged.append(shift_df(total,L,x_var))
    matrices = []
    col_name = 'Lagged ' + str(x_var)
    for lag in lagged:
        merged = total.merge(lag,on=['TICKER','Year + Month'])
        merged[col_name] = [to_float(to) for to in merged[col_name].values]
        matrices.append(merged.dropna())
    regs = []
    for matrix in matrices:
        reg = LinearRegression().fit(matrix[[col_name]], matrix[[y_var]])
        regs.append(reg)
    return regs

pairs = [('Turnover','RET'),('Turnover','abnormal_return'),('abnormal_turnover','abnormal_return')]

regressions = {}
for pair in pairs:
    regressions[(pair[0],pair[1])] = run_return_regressions(pair[0],pair[1])

# once I have these regressions - what do I do with them again?

# Include performance in firm_chars

firm_chars_perf = pd.merge(firm_chars, returns, on = ['TICKER','Year + Month']).dropna()

Y = firm_chars_perf[['Turnover']]
X = firm_chars_perf.drop(['date','Turnover','TICKER','Year + Month','abnormal_turnover','PERMNO','sprtrn','abnormal_return'],axis=1)

reg = LinearRegression().fit(X, Y)
predictions = reg.predict(X)
abnormal_turnover_perf = Y - predictions

firm_chars_perf['abnormal_turnover'] = abnormal_turnover_perf

perf_regressions = run_return_regressions(firm_chars_perf,'abnormal_turnover','abnormal_return')

# Intermediate checking code

repl_check = pd.read_csv("/Users/jacquelinewood/Documents/URAP/replication-check-intermediate.csv")

repl_check.columns = ['(Ticker, Year + Month)','ret','abn_ret','log_size','ind','price','bm','join','depart','turnover','abn_turnover']

def clean_tickyearmo(val):
    first = val.split()[0]
    first = first.replace("(","")
    first = first.replace(",","")
    second = val.split()[1]
    second = second.replace(".","")
    second = int(second.replace(")",""))
    return tuple((first,second))

repl_check['(Ticker, Year + Month)'] = [clean_tickyearmo(tup) for tup in repl_check['(Ticker, Year + Month)'].values]

def turnover_check(ticker, year_mo):
    index = tuple((ticker,year_mo))
    print(index)
    to = turnover.loc[(turnover['Stock Symbol'] == ticker) & (turnover['Year + Month'] == year_mo)]["Turnover"].values[0]
    print("Found turnover: " + str(to))
    check_to = repl_check.loc[repl_check['(Ticker, Year + Month)'] == index]['turnover'].values[0]
    print("Turnover to check: " + str(check_to))
    print(math.isclose(to,check_to,rel_tol=.05))

for tups in repl_check['(Ticker, Year + Month)'].values:
    turnover_check(tups[0],tups[1])

def bmr_check(ticker,year_mo):
    index = tuple((ticker,year_mo))
    print(index)
    try:
        bmr = sorted_merged.loc[(sorted_merged['TICKER'] == ticker) & (sorted_merged['Year + Month'] == year_mo)]["Book to Market Ratio"].values[0]
        print("Found bmr: " + str(bmr))
        check_bmr = float(repl_check.loc[repl_check['(Ticker, Year + Month)'] == index]['bm'].values[0])
        print("BMR to check: " + str(check_bmr))
        print(math.isclose(bmr,check_bmr,rel_tol=.05))
    except:
        print("Not in table")

for tups in repl_check['(Ticker, Year + Month)'].values:
    bmr_check(tups[0],tups[1])

def book_mv_check(ticker,year_mo):
    index = tuple((ticker,year_mo))
    print(index)
    try:
        book = sorted_merged.loc[(sorted_merged['TICKER'] == ticker) & (sorted_merged['Year + Month'] == year_mo)]["ceqq"].values[0]
        print("Found book: " + str(book))
        check_book = float(repl_check.loc[repl_check['(Ticker, Year + Month)'] == index]['book'].values[0])
        print("Book to check: " + str(check_book))
        print(math.isclose(book,check_book,rel_tol=.05))
        
        market = sorted_merged.loc[(sorted_merged['TICKER'] == ticker) & (sorted_merged['Year + Month'] == year_mo)]["Market Value"].values[0]
        print("Found market: " + str(market))
        check_market = float(repl_check.loc[repl_check['(Ticker, Year + Month)'] == index]['market'].values[0])
        print("Market to check: " + str(check_market))
        print(math.isclose(market,check_market))
    except:
        print("Not in table")

for tups in repl_check['(Ticker, Year + Month)'].values:
    book_mv_check(tups[0],tups[1])

def abn_turnover_check(ticker, year_mo):
    index = tuple((ticker,year_mo))
    print(index)
    abn_to = firm_chars.loc[(firm_chars['TICKER'] == ticker) & (firm_chars['Year + Month'] == year_mo)]["abnormal_turnover"].values[0]
    print("Found abn_turnover: " + str(abn_to))
    check_abn_to = repl_check.loc[repl_check['(Ticker, Year + Month)'] == index]['abn_turnover'].values[0]
    print("Abn_turnover to check: " + str(check_abn_to))
    print(math.isclose(abn_to,check_abn_to,rel_tol=.05))

for tups in repl_check['(Ticker, Year + Month)'].values:
    abn_turnover_check(tups[0],tups[1])

# Portfolio work

portfolios = {}
for year_mo in sorted_merged['Year + Month'].unique():
    month = sorted_merged.loc[sorted_merged['Year + Month']==year_mo]
    month = month.sort_values(['abnormal_turnover'])
    top_cutoff = np.nanquantile(month['abnormal_turnover'],0.8)
    shorts = month.loc[month['abnormal_turnover'] >= top_cutoff]
    short = np.average(shorts['abnormal_turnover'])
    bottom_cutoff = np.nanquantile(month['abnormal_turnover'],0.2)
    longs = month.loc[month['abnormal_turnover'] <= bottom_cutoff]
    long = np.average(longs['abnormal_turnover'])
    net_return = long - short
    portfolios[year_mo] = (net_return)

