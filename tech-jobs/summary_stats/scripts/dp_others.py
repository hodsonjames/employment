import re
import unicodecsv as csv
import pandas as pd
import itertools
import numpy as np

from entryProcessor import entryProcessor

empl_file = r"../data/deloitte_pwc.csv"

## Initialize.
career = entryProcessor(None, ticker = ['D', 'P'])

## Iterate.
empl_changes_lst = []
with open(empl_file,"rb") as f:
    reader = csv.reader(f,encoding='utf-8',escapechar='',delimiter='\t')
    for idx, entry in enumerate(itertools.chain(reader,[[None]*33])):
        if idx == np.inf: # End point.
            break
        if entry[3] not in ["-1","Accounting and Auditing"] and entry[26] == "False" and not sum([
                            re.search(r"(?i)\W{}\W".format(x)," "+entry[17]+" ") is not None 
                            for x in ["intern","internship","trainee"]]):
            empl_change_this = career.read(entry)
            if empl_change_this != []:
                empl_changes_lst += empl_change_this

varlist = [
    "type","ticker","yrmth","birth","gender","skill1","skill2","cntry","edu","f_elite",
    "job_role","depmt","ind_next","tenure","nprom"
]

empl_changes_df = pd.DataFrame(data=empl_changes_lst,columns=varlist)
empl_changes_df.to_csv(r'../outputs/dp_others_data.csv')
