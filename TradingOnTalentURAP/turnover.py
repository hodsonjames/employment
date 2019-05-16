
import pandas as pd
import numpy as np
import math
from scipy.stats import mstats
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from scipy import stats


# # Download turnover data

current = pd.read_csv("/Users/jacquelinewood/Documents/URAP/fastwhitepaper_month_current.csv",sep='\t',header=None)
join = pd.read_csv("/Users/jacquelinewood/Documents/URAP/fastwhitepaper_month_join.csv",sep='\t',header=None)
leave = pd.read_csv("/Users/jacquelinewood/Documents/URAP/fastwhitepaper_month_leave.csv",sep='\t',header=None)

col_names = ['Stock Symbol','Year + Month','# Employees','Average Age','# People with Known Age','# Female','# Male','# with No Skills Listed','Average Tenure','Comma-separated Skills Frequencies']

current.columns = col_names
join.columns = col_names
leave.columns = col_names

current = current.loc[(current['Year + Month'] >= 200001)]
join = join.loc[(join['Year + Month'] >= 200001)]
leave = leave.loc[(leave['Year + Month'] >= 200001)]


# # Compute turnover variables from the three data files

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


# # Winsorize turnover variable

turn = mstats.winsorize(turn, limits=(.01,.01))
turnover['Turnover'] = turn

turnover = turnover.dropna(subset=['Turnover'])


# # Read in CRSP data

column_names = ['N/A','Date','N/A','Ticker','N/A','N/A','Industry','N/A','N/A','N/A','Price','Trading Volume','Return','Shares Outstanding','S&P 500 Return']
crsp = pd.read_table("/Users/jacquelinewood/Documents/URAP/CRSP_2000_2016.txt",names=column_names)
crsp = crsp[['Date', 'Ticker', 'Industry', 'Price', 'Trading Volume', 'Return', 'Shares Outstanding', 'S&P 500 Return']]
crsp['Date'] = [int(str(date)[:-2]) for date in crsp['Date'].values]
crsp["Industry"] = pd.to_numeric(crsp["Industry"].str.slice(0, 2), errors='coerce').fillna(0).astype(np.int64)
crsp = crsp[crsp['Industry'] != 0]
crsp = crsp.rename(columns={"Date": "Year + Month", "Ticker": "TICKER","Price":"PRC","Shares Outstanding":"SHROUT","Industry":"NAICS","Return":"RET","S&P 500 Return":"sprtrn","Trading Volume":"VOL"})

crsp['Market Value'] = crsp['PRC'] * crsp['SHROUT']
crsp = crsp[crsp['Market Value'] > 0]
crsp['Size'] = np.log(crsp['Market Value'])


# # Read in Compustat

column_names = ['gvkey','datadate','fyearq','fqtr','indfmt','consol','popsrc','datafmt','tic','cusip','curcdq','datacqtr','datafqtr','rdq','ceqq','cshoq','epsf12','epsfxq','xrdq','costat','prccq','naics']
compustat = pd.read_table("/Users/jacquelinewood/Documents/URAP/Compustat_2000_2016.txt",names=column_names)

compustat['ceqq'] = compustat['ceqq'] * 1000 #said it was in millions but this is what makes it equal intermediate values?
compustat['Year + Month'] = [int(str(date)[:-2]) for date in compustat['datadate'].values]
compustat.loc[compustat['tic'] == 'GOOGL', 'tic'] = 'GOOG'


# # Merge data

merged = pd.merge(crsp, compustat, how = 'outer', left_on = ['TICKER','Year + Month'], right_on = ['tic','Year + Month'])


# # Book to market ratio

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
    
    for mo in begin_mos:
        quart  = quart.set_value(mo, 'ceqq', np.nan)
    frontfill_ceqqs = quart[['ceqq']].fillna(method='ffill')
    quart[['ceqq']] = frontfill_ceqqs
    
    backfill_ceqqs = quart[['ceqq']].fillna(method='bfill')
    quart[['ceqq']] = backfill_ceqqs
    
    
    quarts.append(quart)
back = pd.concat(quarts).reset_index().sort_values(by = ['TICKER','Year + Month'])
merged = pd.merge(merged,back,on=['TICKER','Year + Month']).drop(['datafqtr_x','ceqq_x'], axis=1).rename(columns={'datafqtr_y': 'datafqtr','ceqq_y':'ceqq'})

merged = merged.sort_values(by = ['TICKER','Year + Month'])

merged.head()

def calc_bmratio(row):
    book_val = row['ceqq']
    mkt_val = row['Market Value']
    return book_val / mkt_val

ratio = []
for index, row in merged.iterrows():
    try:
        ratio.append(calc_bmratio(row))
    except:
        ratio.append(np.nan)

merged['Book to Market Ratio'] = ratio

def to_float(val):
    try:
        return float(val)
    except:
        return np.nan

merged['Book to Market Ratio'] = [to_float(bmr) for bmr in merged['Book to Market Ratio'].values]


# # Intermediate check

repl_check = pd.read_csv("/Users/jacquelinewood/Documents/URAP/replication_check_intermediate.csv")

repl_check.columns = ['(Ticker, Year + Month)','ret','abn_ret','log_size','ind','price','book','market','bm','join','depart','turnover','abn_turnover']

def clean_tickyearmo(val):
    first = val.split()[0]
    first = first.replace("(","")
    first = first.replace(",","")
    second = val.split()[1]
    second = second.replace(".","")
    second = int(second.replace(")",""))
    return tuple((first,second))

repl_check['(Ticker, Year + Month)'] = [clean_tickyearmo(tup) for tup in repl_check['(Ticker, Year + Month)'].values]

repl_check['ret'] = [item[:-1] if item[-1]=='�' else item for item in repl_check['ret'].values]
repl_check['abn_ret'] = [item[:-1] if item[-1]=='�' else item for item in repl_check['abn_ret'].values]
repl_check['log_size'] = [item[:-1] if item[-1]=='�' else item for item in repl_check['log_size'].values]
repl_check['ind'] = [item[:-1] if item[-1]=='�' else item for item in repl_check['ind'].values]
repl_check['price'] = [item[:-1] if item[-1]=='�' else item for item in repl_check['price'].values]
repl_check['bm'] = [item[:-1] if item[-1]=='�' else item for item in repl_check['bm'].values]

def size_check(ticker, year_mo):
    index = tuple((ticker,year_mo))
    print(index)
    try:
        size = merged.loc[(merged['TICKER'] == ticker) & (merged['Year + Month'] == year_mo)]["Size"].values[0]
        print("Found size: " + str(size))
        check_size = float(repl_check.loc[repl_check['(Ticker, Year + Month)'] == index]['log_size'].values[0])
        print("Size to check: " + str(check_size))
        print(math.isclose(size,check_size,rel_tol=.05))
    except:
        print("Not in table")

for tups in repl_check['(Ticker, Year + Month)'].values:
    size_check(tups[0],tups[1])

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
        bmr = merged.loc[(merged['TICKER'] == ticker) & (merged['Year + Month'] == year_mo)]["Book to Market Ratio"].values[0]
        print("Found bmr: " + str(bmr))
        check_bmr = float(repl_check.loc[repl_check['(Ticker, Year + Month)'] == index]['bm'].values[0])
        print("BMR to check: " + str(check_bmr))
        print(math.isclose(bmr,check_bmr,rel_tol=.05))
    except:
        print("Not in table")

for tups in repl_check['(Ticker, Year + Month)'].values:
    bmr_check(tups[0],tups[1])


# # Making firm characteristics

grouped_industries = merged.groupby(['TICKER'])['NAICS'].apply(max)

industries = dict(grouped_industries)

ind = []
for index, row in merged.iterrows():
    try:
        ind.append(industries[row['TICKER']])
    except:
        ind.append(np.nan)

industry_dummy = pd.get_dummies(merged['NAICS'])

firm_chars = pd.concat([merged[['TICKER','Year + Month','Size','Book to Market Ratio']],industry_dummy], axis=1)
firm_chars = pd.merge(firm_chars,turnover[['Stock Symbol','Year + Month','Turnover']],'inner',left_on=['TICKER','Year + Month'],right_on = ['Stock Symbol','Year + Month']).drop(['Stock Symbol'], axis=1)
firm_chars = firm_chars.dropna()


# # 5. Compute abnormal turnover : regress turnover on firm characteristics and take residuals

Y = firm_chars['Turnover']
X = firm_chars.drop(['Turnover','TICKER','Year + Month'],axis=1)

X = sm.add_constant(X)

model = sm.OLS(Y,X)
results = model.fit()
ypred = results.fittedvalues
abnormal_turnover = Y - ypred

firm_chars['abnormal_turnover'] = abnormal_turnover

turnover = pd.merge(turnover,firm_chars[['TICKER','Year + Month','abnormal_turnover']],left_on=['Stock Symbol','Year + Month'],right_on = ['TICKER','Year + Month']).drop(columns={'TICKER'})

# # Check abnormal turnover values

def abn_turnover_check(ticker, year_mo):
    index = tuple((ticker,year_mo))
    print(index)
    abn_to = firm_chars.loc[(firm_chars['TICKER'] == ticker) & (firm_chars['Year + Month'] == year_mo)]["abnormal_turnover"].values[0]
    print("Found abn_turnover: " + str(abn_to))
    check_abn_to = repl_check.loc[repl_check['(Ticker, Year + Month)'] == index]['abn_turnover'].values[0]
    print("Abn_turnover to check: " + str(check_abn_to))
    print(math.isclose(abn_to,check_abn_to,rel_tol=.05))

repl_check['(Ticker, Year + Month)'].values

for tups in repl_check['(Ticker, Year + Month)'].values:
    abn_turnover_check(tups[0],tups[1])

abn_to = {}
for tups in repl_check['(Ticker, Year + Month)'].values:
    abn_to[(tups[0],tups[1])] = firm_chars.loc[(firm_chars['TICKER'] == tups[0]) & (firm_chars['Year + Month'] == tups[1])]["abnormal_turnover"].values[0]
    print(str([(tups[0],tups[1])]) + ":" + str(abn_to[(tups[0],tups[1])]))


# # Back to Business - Returns

total = pd.merge(merged,turnover,left_on=['TICKER','Year + Month'],right_on = ['Stock Symbol','Year + Month'])

total['RET'] = [to_float(ret) for ret in total['RET'].values]

total['abnormal_return'] = total['RET'] - total['sprtrn']

def shift_y(total,lag,y_column):
    grouped = pd.DataFrame(total.groupby(['TICKER','Year + Month'])[y_column].agg(item))
    shifted_dfs = []
    tickers = grouped.index.get_level_values('TICKER').unique()
    for ticker in tickers:
        shifted = grouped.loc[ticker].shift(lag)
        shifted['TICKER'] = np.repeat(ticker,len(shifted))
        shifted_dfs.append(shifted)
    lagged = pd.concat(shifted_dfs).reset_index().sort_values(by = ['TICKER','Year + Month'])
    
    lagged[y_column] = [to_float(to) for to in lagged[y_column].values]
    
    lagged = lagged.rename(columns={y_column: "Lagged " + y_column})
    return lagged

def run_return_regressions(total,x_var,y_var):
    lags = [1,2,3,6]
    lagged_ys = []
    for L in lags:
        lagged_ys.append(shift_y(total,L,y_var))
    matrices = []
    col_name = 'Lagged ' + str(y_var)
    for lag in lagged_ys:
        merged = total.merge(lag,on=['TICKER','Year + Month'])
        merged = merged[[x_var,col_name]]
        merged = merged.dropna()
        matrices.append(merged)
    coefs = []
    ses = []
    for matrix in matrices:
        y = matrix[[col_name]]
        X = matrix[[x_var]]
        X = sm.add_constant(X)
        model = sm.OLS(y,X)
        results = model.fit()
        coef = results.params[1]
        se = results.bse[1]
        coefs.append(coef)
        ses.append(se)
    return coefs,ses

pairs = [('Turnover','RET'),('Turnover','abnormal_return'),('abnormal_turnover','abnormal_return')]

coefs = {}
ses = {}
for pair in pairs:
    print(str(pair))
    params = run_return_regressions(total,pair[0],pair[1])
    coef = params[0]
    se = params[1]
    coefs[(pair[0],pair[1])] = [str((item/10)*100) + "%" for item in coef]
    ses[(pair[0],pair[1])] = [str((item/10)*100) + "%" for item in se]

coefficients = pd.DataFrame.from_dict(coefs)
coefficients.columns = pairs
coefficients.index = ["L = 1 month coefficient","L = 2 months coefficient","L = 3 months coefficient","L = 6 months coefficient"]

standard_errors = pd.DataFrame.from_dict(ses)
standard_errors.columns = pairs
standard_errors.index = ["L = 1 month standard error","L = 2 months standard error","L = 3 months standard error","L = 6 months standard error"]


# # Include performance in firm_chars

firm_chars_perf = pd.merge(firm_chars, total[['TICKER','Year + Month','RET','abnormal_return']], on = ['TICKER','Year + Month']).dropna()

Y = firm_chars_perf['Turnover']
X = firm_chars_perf.drop(['TICKER','Year + Month','Turnover','abnormal_turnover','abnormal_return'],axis=1)

X = sm.add_constant(X)

model = sm.OLS(Y,X)
results = model.fit()
ypred = results.fittedvalues
abnormal_turnover_perf = Y - ypred

firm_chars_perf['abnormal_turnover with perf'] = abnormal_turnover_perf

total = pd.merge(total,firm_chars_perf[['TICKER','Year + Month','abnormal_turnover with perf']],on = ['TICKER','Year + Month'])

perf_params = run_return_regressions(firm_chars_perf,'abnormal_turnover with perf','abnormal_return')
perf_coefs = perf_params[0]
perf_coef = [str((item/10)*100) + "%" for item in perf_coefs]
perf_ses = perf_params[1]
perf_se = [str((item/10)*100) + "%" for item in perf_ses]

coefficients[('abnormal_turnover with perf','abnormal_return')] = perf_coef

standard_errors[('abnormal_turnover with perf','abnormal_return')] = perf_se

coefficients = pd.concat([coefficients,standard_errors])
coefficients = coefficients.sort_index(ascending=True)

