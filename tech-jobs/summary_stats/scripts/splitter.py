import sys
import os
import unicodecsv as csv
import pandas as pd
import itertools
import numpy as np


empl_file = '../data/deloitte_pwc.csv'
deloitte = []
pwc = []

id_interest = 'placeholder'
comp_state = ''
with open(empl_file,"rb") as f:
    reader = csv.reader(f,encoding='utf-8',escapechar='',delimiter='\t')
    for idx, entry in enumerate(itertools.chain(reader,[[None]*33])):
        if idx == np.inf: # End point
            break
        if entry[21] == 'D' or (comp_state == 'D' and entry[0] == id_interest):
            if entry[0] != id_interest:
                id_interest = entry[0]
            deloitte.append(entry)
            comp_state = 'D'
        elif entry[21] == 'P' or (comp_state == 'P' and entry[0] == id_interest):
            if entry[0] != id_interest:
                id_interest = entry[0]
            pwc.append(entry)
            comp_state = 'P'

import csv
with open("../data/deloitte_pwc/D.csv", "w", newline="") as f:
    writer = csv.writer(f, dialect = csv.excel_tab)
    writer.writerows(deloitte)

with open("../data/deloitte_pwc/P.csv", "w", newline="") as f:
    writer = csv.writer(f, dialect = csv.excel_tab)
    writer.writerows(pwc)
                