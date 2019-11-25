import re
import sys
import os
import unicodecsv as csv
import pandas as pd
import itertools
import numpy as np
from collections import Counter

import science.roles as r
roles = r.Roles()

empl_path = sys.argv[1] #directory of csv files to process
#target = sys.argv[2] #csv file name to write

## Iterate.
empl_file_lst = os.listdir(empl_path)
for empl_file_name in empl_file_lst:
    empl_file = empl_path + '/' +empl_file_name
    updated = []
    with open(empl_file,"rb") as f:
        reader = csv.reader(f,encoding='utf-8',escapechar='',delimiter='\t')
        current_id = ''
        entries_per_person = []
        max_edu = 0
        edu_dpmt = set()
        for idx, entry in enumerate(itertools.chain(reader,[[None]*33])):
            if idx == np.inf: # End point
                break
            # Some datasets have extra column of employee names
            # Drop entry[1] if it contains employee name instead of birth year  
            if len(entry) > 33:
                del entry[1]

            if entry[0] != current_id:
                # append and reset
                e_dpmt = ','
                e_dpmt = e_dpmt.join(edu_dpmt)
                for e in entries_per_person:
                    e[8] = max_edu
                    e[29] = e_dpmt # I think 29th column had no use previously? 
                    updated.append(e)
                current_id = entry[0]
                del entries_per_person[:]
                max_edu = 0
                edu_dpmt.clear()

            if entry[26] == 'False': # employment data
                match = re.search(r",\s?([\s\w,]*)",entry[17])
                if (match is not None):
                    normalized_title = match.group(1)
                else:
                    normalized_title = entry[17]
                try:
                    entry[18] = roles.parse_work(normalized_title).departments.pop() #is this appropriate? 
                except:
                    pass
                entries_per_person.append(entry)
            elif entry[26] == 'True': #education data
                query = roles.parse_edu(entry[20], entry[17])
                max_edu = max(max_edu, query.level)
                # add department
                for f in query.faculties:
                    edu_dpmt.add(f)
                entries_per_person.append(entry)
    with open(empl_file + "_updated.csv", "w", newline="") as f:
        writer = csv.writer(f, dialect = csv.excel_tab)
        writer.writerows(updated)
