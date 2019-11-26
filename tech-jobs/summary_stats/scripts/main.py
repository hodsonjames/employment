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

empl_path = sys.argv[1] #directory of csv files to process
primary_skills = sys.argv[2].split(',') # filter by primary skill, "all" for alll skills, -(skill) to exclude
target = sys.argv[3] #csv file name to write

exclusive = False
if primary_skills[0][0] == '-':
    exclusive = True
    all_skills_but = []
    for skill in primary_skills:
        all_skills_but.append(re.sub(r'[-()]','', skill))
    all_skills_but.append('-1')

## Initialize. Tickers include companies of interest
rec = Records()
employee = Employee() # default empty employee
processor = EntryProcessor(employee, rec)

#block for annual counts. 
empl_file_lst = os.listdir(empl_path)
tickers = [file_name[:-4].upper() for file_name in empl_file_lst]
empl_by_year = {}
for ticker in tickers:
    empl_by_year[ticker] = Counter([])
def annualCounter(entry):
    ''' Updates empl_by_year dictionary '''
    if entry[21] in tickers and entry[11] != "None" and (entry[13] != "None" or entry[15] == "True"):
        empl_by_year[entry[21]] += Counter(
            range(
                pd.to_datetime(entry[11]).year,
                pd.to_datetime(entry[13]).year if entry[13]!="None" else 2019
            )
        )


## Iterate.
empl_file_lst = os.listdir(empl_path)
for empl_file_name in empl_file_lst:
    empl_file = empl_path + '/' +empl_file_name
    ticker = empl_file_name[:-4].upper()
    processor.change_ticker(ticker)
    with open(empl_file,"rb") as f:
        reader = csv.reader(f,encoding='utf-8',escapechar='',delimiter='\t')
        for idx, entry in enumerate(itertools.chain(reader,[[None]*33])):
            if idx == np.inf: # End point
                break
            # Some datasets have extra column of employee names
            # Drop entry[1] if it contains employee name instead of birth year  
            if len(entry) > 33:
                del entry[1]
            if entry[26] == 'False': # only consider employment data
                #filter irregular workers
                irregular_worker_filter = [re.search(r"(?i)\W{}\W".format(x)," "+entry[17]+" ") 
                                        is None for x in ["intern","internship","trainee","student"]]
                is_irregular_worker = (sum(irregular_worker_filter) !=4)
                if is_irregular_worker:
                    continue
                elif 'all' in primary_skills and entry[3] != '-1':
                    update = processor.read(entry)
                    annualCounter(entry)
                elif exclusive and entry[3] not in all_skills_but:
                    update = processor.read(entry)
                    annualCounter(entry)
                elif entry[3] in primary_skills:
                    update = processor.read(entry)
                    annualCounter(entry)

empl_changes_lst = rec.output()
varlist = [
    "type","ticker","yrmth","birth","gender","skill1","skill2","cntry","edu","f_elite", "edu_faculty",
    "job_role","depmt","ind_next","tenure","nprom"
]

empl_changes_df = pd.DataFrame(data=empl_changes_lst,columns=varlist)
empl_changes_df.to_csv(r'../outputs/' + target + '.csv', index= False)

empl_by_year = pd.DataFrame(empl_by_year).fillna(0).unstack().reset_index()
empl_by_year.columns = ["ticker", "year", "employment"]
empl_by_year.to_csv(r'../outputs/' + target + '_by_year.csv', index= False)
