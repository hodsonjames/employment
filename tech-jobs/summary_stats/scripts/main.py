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

try:
    assert len(sys.argv) == 5
except AssertionError:
    print('''Correct usage: 
    python main.py (directory containing data) (target) (primary skills) (infer tickers) 
    target: name of file to be written under outputs 
    primary_skills: filter by primary skill, with options "all" for every skills, -(skill) to exclude 
    infer_tickers: Either True or comma separated list of normalizaed tickers. 
                   If True, the files under directory are expected to be named as
                   the corresponding tickers of interest.
                   '''
    )
    sys.exit(1)
    
empl_path = sys.argv[1] #directory of files to process
target = sys.argv[2] #csv file name to write
primary_skills = sys.argv[3].split(',') # 
infer_tickers = sys.argv[4]
if infer_tickers != 'True':
    tickers = infer_tickers.split(',')
    infer_tickers = False
else:
    try:
        empl_file_lst = os.listdir(empl_path)
        tickers = [os.path.splitext(file_name)[0].upper() for file_name in empl_file_lst]
        infer_tickers = True
    except NotADirectoryError:
        print('NOT SUPPORTED: Tickers must be specified to run directly on data file')
        sys.exit(1)

## Initialize. Tickers include companies of interest
rec = Records()
employee = Employee() # default empty employee
processor = EntryProcessor(employee, rec, tickers)

empl_by_year = {}
for ticker in tickers:
    empl_by_year[ticker] = Counter([])

if os.path.isdir(empl_path):
    if os.listdir(empl_path)[0].endswith('.csv'):
        csv_parser(processor, empl_by_year, empl_path, tickers, infer_tickers, primary_skills)
    else:
        json_parser(processor, empl_by_year, empl_path, tickers, infer_tickers, primary_skills)
else:
    if empl_path.endswith('.csv'):
        print('Individual file processing supported only on json')
        sys.exit(1)
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
