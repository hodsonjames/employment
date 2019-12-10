import re
import sys
import os
import unicodecsv as csv
import pandas as pd
import itertools
import numpy as np
from collections import Counter

from entryProcessor import EntryProcessor
from employee import Employee
from records import Records
from csv_parser  import csv_parser
from json_parser import json_parser

assert len(sys.argv) == 5, \
    '''Correct usage: 
    python main.py (directory_containing_data) (target) (primary_skills) (infer_tickers) 
    target: name of file to be written under outputs 
    primary_skills: filter by primary skill, "all" for alll skills, -(skill) to exclude 
    infer_tickers: Either True or comma separated list of normalizaed tickers'''
    
empl_path = sys.argv[1] #directory of files to process
target = sys.argv[2] #csv file name to write
primary_skills = sys.argv[3].split(',') # 
infer_tickers = sys.argv[4]
if infer_tickers != 'True':
    infer_tickers = False
    tickers_interest = infer_tickers.split(',')
else:
    infer_tickers = True
    tickers_interest = []


## Initialize. Tickers include companies of interest
rec = Records()
employee = Employee() # default empty employee
processor = EntryProcessor(employee, rec, tickers_interest)

empl_file_lst = os.listdir(empl_path)
if infer_tickers:
    tickers = [file_name[:-5].upper() for file_name in empl_file_lst]
else:
    tickers = tickers_interest
empl_by_year = {}
for ticker in tickers:
    empl_by_year[ticker] = Counter([])

if os.listdir(empl_path)[0].endswith('.csv'):
    csv_parser(processor, empl_by_year, empl_path, tickers, infer_tickers, primary_skills)
else:
    json_parser(processor, empl_by_year, empl_path, tickers, infer_tickers, primary_skills)

#block for annual counts. 
empl_changes_lst = rec.output()
varlist = [
    "type","ticker","yrmth", "birth","gender","skill1","skill2","cntry","edu","f_elite",
    "edu_faculty","raw_skills", "job_role","depmt","ind_next","tenure","nprom"
]

empl_changes_df = pd.DataFrame(data=empl_changes_lst,columns=varlist)
empl_changes_df.to_csv(r'../outputs/' + target + '.csv', index= False)

empl_by_year = pd.DataFrame(empl_by_year).fillna(0).unstack().reset_index()
empl_by_year.columns = ["ticker", "year", "employment"]
empl_by_year.to_csv(r'../outputs/' + target + '_by_year.csv', index= False)
