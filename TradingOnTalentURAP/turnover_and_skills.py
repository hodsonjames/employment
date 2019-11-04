import pandas as pd
import numpy as np
import math
from scipy.stats import mstats
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from scipy import stats
import statsmodels
import ast


# Turnover

# Import turnover data

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


# Compute turnover

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


# Winsorize turnover

turn = mstats.winsorize(turn, limits=(.01,.01))
turnover['Turnover'] = turn

turnover = turnover.dropna(subset=['Turnover'])


# Read in CRSP data

column_names = ["PERMNO","date","SHRCD","TICKER","COMNAM","NAICS","CUSIP","DLSTCD","ACPERM","DLPRC","PRC","VOL","RET","SHROUT","sprtrn"]
crsp = pd.read_table("/Users/jacquelinewood/Documents/URAP/CRSP_2000_2016.txt",names=column_names)

crsp = crsp[['date', 'TICKER','PRC', 'VOL', 'RET', 'SHROUT', 'sprtrn']]
crsp['Year + Month'] = [int(str(date)[:-2]) for date in crsp['date'].values]
crsp['Market Value'] = crsp['PRC'] * crsp['SHROUT']
crsp['Size'] = np.log(crsp['Market Value'])
crsp.TICKER[crsp.TICKER=="GOOGL"] = "GOOG"


# Read in Compustat data

column_names = ['gvkey','datadate','fyearq','fqtr','indfmt','consol','popsrc','datafmt','tic','cusip','curcdq','datacqtr','datafqtr','rdq','ceqq','cshoq','epsf12','epsfxq','xrdq','costat','prccq','naics']
compustat = pd.read_table("/Users/jacquelinewood/Documents/URAP/Compustat_2000_2016.txt",names=column_names)

compustat['ceqq'] = compustat['ceqq'] * 1000 #said it was in millions but this is what makes it equal intermediate values?
compustat['Year + Month'] = [int(str(date)[:-2]) for date in compustat['datadate'].values]
compustat.loc[compustat['tic'] == 'GOOGL', 'tic'] = 'GOOG'

def to_float(val):
    try:
        return float(val)
    except:
        return np.nan


compustat['naics'] = [to_float(str(ind)[:2]) for ind in compustat['naics']]


# Calculate BMR

merged = crsp

subsets = {}
quarter_end_mos = {}
industries = {}
for ticker in set(compustat['tic']):
    
    if ticker is not np.nan:
    
        subset = compustat.loc[compustat['tic'] == ticker]
        subsets[ticker] = subset
        
        ind = list(set(subset['naics']))[0]
        industries[ticker] = ind
        
        quarter_end_per = sorted(set(subset['Year + Month']))
    
        quarter_end_mos[ticker] = quarter_end_per


ceqqs_to_use = {}
i = 0
test = []
for index, row in merged.iterrows():
    ticker = row['TICKER']
    current_mo = row['Year + Month']
    
    if ticker in quarter_end_mos:
        possible_mos = quarter_end_mos[ticker]
    else:
        continue
    
    less_thans = [date for date in possible_mos if date < current_mo]
    
    if len(less_thans) == 0:
        continue
    
    recent_mo = less_thans[-1]
    
    subset = subsets[ticker]
    
    
    if (current_mo - recent_mo) <= 3:
        ceqq = subset.loc[subset['Year + Month'] == recent_mo]['ceqq'].values[0]
        ceqqs_to_use[(ticker, current_mo)] = ceqq
    elif str(current_mo)[-2:] in ['01','02','03'] and str(recent_mo)[-2:] in ['10','11','12']:
        ceqq = subset.loc[subset['Year + Month'] == recent_mo]['ceqq'].values[0]
        ceqqs_to_use[(ticker, current_mo)] = ceqq
    else:
        continue


ratios = []
for index, row in merged.iterrows():
    ticker = row['TICKER']
    current_mo = row['Year + Month']
    
    if (ticker, current_mo) in ceqqs_to_use:
        book_val = ceqqs_to_use[(ticker, current_mo)]
    else:
        book_val = np.nan
    mkt_val = row['Market Value']
        
    bmr = book_val / mkt_val
    
    ratios.append(bmr)


merged['Book to Market Ratio'] = ratios
merged['Book to Market Ratio'] = [to_float(bmr) for bmr in merged['Book to Market Ratio'].values]


# Add Industry column

industry_rows = []
for index, row in merged.iterrows():
    ticker = row['TICKER']
    
    if ticker in industries:
        ind = industries[ticker]
    else:
        ind = np.nan
        
    industry_rows.append(ind)


merged['NAICS'] = industry_rows


# Make firm characteristics matrix

merged = merged[merged['Book to Market Ratio']>0]

grouped_industries = merged.groupby(['TICKER'])['NAICS'].apply(max)

industries = dict(grouped_industries)

industry_dummy = pd.get_dummies(merged['NAICS'])


firm_chars = pd.concat([merged[['TICKER','Year + Month','Size','Book to Market Ratio']],industry_dummy], axis=1)


firm_chars = pd.merge(firm_chars,turnover[['Stock Symbol','Year + Month','Turnover']],'outer',left_on=['TICKER','Year + Month'],right_on = ['Stock Symbol','Year + Month']).drop(['Stock Symbol'], axis=1)


firm_chars = firm_chars.dropna()


# Compute abnormal turnover

Y = firm_chars['Turnover']
X = firm_chars.drop(['Turnover','TICKER','Year + Month'],axis=1)


model = sm.OLS(Y,X)
results = model.fit()
ypred = results.fittedvalues
abnormal_turnover = Y - ypred

firm_chars['abnormal_turnover'] = abnormal_turnover


turnover = pd.merge(turnover,firm_chars[['TICKER','Year + Month','abnormal_turnover']],left_on=['Stock Symbol','Year + Month'],right_on = ['TICKER','Year + Month']).drop(columns={'TICKER'})


# Construct total

total = pd.merge(merged,turnover,left_on=['TICKER','Year + Month'],right_on = ['Stock Symbol','Year + Month'])


total = total.sort_values(['TICKER','Year + Month'])


total['RET'] = [to_float(ret) for ret in total['RET'].values]


total['abnormal_return'] = total['RET'] - total['sprtrn']


# Calculate momentum

def get_x_months_ago(t, x):
    t = str(t)
    year = int(t[:4])
    month = int(t[-2:])
    
    new_month = month - x
    
    if x == 12:
        new_year = year - 1
        new_month = month
    elif new_month == 0:
        new_month = 12
        new_year = year - 1
    else:
        new_year = year
        
    new_year = str(new_year)
    new_month = str(new_month)
        
    if len(new_month) == 1:
        new_month = '0' + new_month
    
    return int(new_year + new_month)


def calc_mom(t_1, t_12):
    
    mom = (t_1 - t_12) / t_12
    
    return mom


prices = {}
for index, row in total.iterrows():
    tic = row['TICKER']
    date = row['Year + Month']
    prc = row['PRC']
    
    prices[(tic, date)] = prc


momentum = {}
for pair in prices:
    tic = pair[0]
    date = pair[1]
    
    t_1 = get_x_months_ago(date, 1)
    t_12 = get_x_months_ago(date, 12)
    
    if (tic, t_1) in prices:
        prc_1 = prices[(tic, t_1)]
    else:
        prc_1 = np.nan
        
    if (tic, t_12) in prices:
        prc_12 = prices[(tic, t_12)]
    else:
        prc_12 = np.nan
    
    mom = calc_mom(prc_1, prc_12)
    
    momentum[pair] = mom


moms = []
for index, row in total.iterrows():
    tic = row['TICKER']
    date = row['Year + Month']
    
    mom = momentum[(tic, date)]
    
    moms.append(mom)


total['mom'] = moms
total = total.dropna()


# Run regressions

def item(value):
    return value


all_mos = sorted(set(total['Year + Month']))


def shift_y(total,lag,y_column):
    grouped = pd.DataFrame(total.groupby(['TICKER','Year + Month'])[y_column].agg(item))
    shifted_dfs = []
    tickers = grouped.index.get_level_values('TICKER').unique()
    for ticker in tickers:
        subset = grouped.loc[ticker]
        subset = subset.reindex(all_mos)
        shifted = subset.shift(lag)
        shifted['TICKER'] = np.repeat(ticker,len(shifted))
        shifted_dfs.append(shifted)
    lagged = pd.concat(shifted_dfs).reset_index().sort_values(by = ['TICKER','Year + Month'])
    
    lagged[y_column] = [to_float(to) for to in lagged[y_column].values]
    
    lagged = lagged.rename(columns={y_column: "Lagged " + y_column})
    return lagged


def run_return_regressions(total,x_var,y_var):
    lags = [-1,-2,-3,-6]
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


# 4th regression with momentum

firm_chars_perf = pd.merge(firm_chars, total[['TICKER','Year + Month','mom']], on = ['TICKER','Year + Month']).dropna()


Y = firm_chars_perf['Turnover']
X = firm_chars_perf.drop(['TICKER','Year + Month','Turnover','abnormal_turnover'],axis=1)


model = sm.OLS(Y,X)
results = model.fit()
ypred = results.fittedvalues
abnormal_turnover = Y - ypred


firm_chars_perf['abnormal_turnover_with_perf'] = abnormal_turnover


total = pd.merge(total, firm_chars_perf[['TICKER','Year + Month','abnormal_turnover_with_perf']], on = ['TICKER','Year + Month']).dropna()


perf_params = run_return_regressions(total,'abnormal_turnover_with_perf','abnormal_return')


perf_coefs = perf_params[0]
perf_coef = [str((item/10)*100) + "%" for item in perf_coefs]
perf_ses = perf_params[1]
perf_se = [str((item/10)*100) + "%" for item in perf_ses]

coefficients[('abnormal_turnover with perf','abnormal_return')] = perf_coef
standard_errors[('abnormal_turnover with perf','abnormal_return')] = perf_se

coefficients = pd.concat([coefficients,standard_errors])
coefficients = coefficients.sort_index(ascending=True)


# Skills

# Import data

current = pd.read_csv("/Users/jacquelinewood/Documents/URAP/fastwhitepaper_month_current.csv",sep='\t',header=None)

col_names = ['Stock Symbol','Year + Month','# Employees','Average Age','# People with Known Age','# Female','# Male','# with No Skills Listed','Average Tenure','Comma-separated Skills Frequencies']
current.columns = col_names

current = current.loc[(current['Year + Month'] >= 200001)]

skills = {"Business Development":47,
"Product Management":21,
"Administration":36,
"Human Resources (Jr)":10,
"Human Resources (Sr)":11,
"Sales":23,"CRM":40,
"Sales Management":49,
"Digital Marketing":4,
"Social Media":25,
"Public Policy":46,
"Accounting & Auditing":35,
"Banking & Finance":44,
"Insurance":24,
"Web Development":26,
"Mobile":42,
"Data Analysis":13,
"Web Design":45,
"Graphic Design":30,
"Video & Film":39}


skill_indices = list(skills.values())

skill_col = list(current['Comma-separated Skills Frequencies'])

current['Comma-separated Skills Frequencies'] = [ast.literal_eval(item) for item in skill_col]

updated_skill_col = list(current['Comma-separated Skills Frequencies'])

current['Comma-separated Skills Frequencies'] = [[item[i] for i in skill_indices] for item in updated_skill_col]


# Include abnormal_return in current

current = pd.merge(current, crsp[['TICKER','Year + Month','RET','sprtrn']], left_on = ['Stock Symbol','Year + Month'], right_on = ['TICKER','Year + Month']).dropna()


current['RET'] = [to_float(ret) for ret in current['RET'].values]


current['abnormal_return'] = current['RET'] - current['sprtrn']


# Winsorize skills

skill_col = list(current['Comma-separated Skills Frequencies'])


num_per_skill = np.array(skill_col).T.tolist()


winsorized_skills = [mstats.winsorize(item, limits=(.01,.01)) for item in num_per_skill]


column_winsorized_skills = np.array(winsorized_skills).T

# Calculate abnormal skill

updated_firm_chars = firm_chars_perf.drop(['Turnover','abnormal_turnover','abnormal_turnover_with_perf','mom'], axis=1)


with_abn_skill = []
for skill in winsorized_skills:
    current['current skill'] = skill
    
    firm_chars_for_skill = pd.merge(updated_firm_chars, current[['Stock Symbol','Year + Month','current skill','abnormal_return']], left_on = ['TICKER','Year + Month'], right_on = ['Stock Symbol','Year + Month']).drop(['Stock Symbol'],axis=1)
    
    Y = firm_chars_for_skill['current skill']
    X = firm_chars_for_skill.drop(['current skill','TICKER','Year + Month','abnormal_return'],axis=1)
    X = sm.add_constant(X)
    
    model = sm.OLS(Y,X)
    results = model.fit()
    ypred = results.fittedvalues
    
    abnormal_skill = Y - ypred
    firm_chars_for_skill['abnormal_skill'] = abnormal_skill
    
    with_abn_skill.append(firm_chars_for_skill)


# Run regressions

coefs = {}
ses = {}
for i in range(len(with_abn_skill)):
    skill_strings = list(skills.keys())
    params = run_return_regressions(with_abn_skill[i],'abnormal_skill','abnormal_return')
    coef = params[0]
    se = params[1]
    coefs[skill_strings[i]] = [str((item/10)*100) + "%" for item in coef]
    ses[skill_strings[i]] = [str((item/10)*100) + "%" for item in se]


coefficients = pd.DataFrame.from_dict(coefs,orient='index')
coefficients.columns = ["L = 1 month","L = 2 months","L = 3 months","L = 6 months"]
coefficients.index = [item + " Coefficient" for item in coefficients.index]


standard_errors = pd.DataFrame.from_dict(ses,orient='index')
standard_errors.columns = ["L = 1 month","L = 2 months","L = 3 months","L = 6 months"]
standard_errors.index = [item + " Standard Error" for item in standard_errors.index]


coefficients = pd.concat([coefficients,standard_errors])


new_index= ['Business Development Coefficient',
            'Business Development Standard Error',
 'Product Management Coefficient',
            'Product Management Standard Error',
 'Administration Coefficient',
            'Administration Standard Error',
 'Human Resources (Jr) Coefficient',
            'Human Resources (Jr) Standard Error',
 'Human Resources (Sr) Coefficient',
            'Human Resources (Sr) Standard Error',
 'Sales Coefficient',
            'Sales Standard Error',
 'CRM Coefficient',
            'CRM Standard Error',
 'Sales Management Coefficient',
            'Sales Management Standard Error',
 'Digital Marketing Coefficient',
            'Digital Marketing Standard Error',
 'Social Media Coefficient',
            'Social Media Standard Error',
 'Public Policy Coefficient',
            'Public Policy Standard Error',
 'Accounting & Auditing Coefficient',
             'Accounting & Auditing Standard Error',
 'Banking & Finance Coefficient',
            'Banking & Finance Standard Error',
 'Insurance Coefficient',
            'Insurance Standard Error',
 'Web Development Coefficient',
            'Web Development Standard Error',
 'Mobile Coefficient',
            'Mobile Standard Error',
 'Data Analysis Coefficient',
            'Data Analysis Standard Error',
 'Web Design Coefficient',
            'Web Design Standard Error',
 'Graphic Design Coefficient',
            'Graphic Design Standard Error',
 'Video & Film Coefficient',
           'Video & Film Standard Error']
coefficients = coefficients.reindex(new_index)
