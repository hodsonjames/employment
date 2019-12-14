import re
import os
import unicodecsv as csv
import pandas as pd
import itertools
import numpy as np
from collections import Counter
import json

from employee import Employee


def json_parser(processor, empl_by_year, empl_path, tickers, infer_tickers, primary_skills):
    #block for annual counts. 
    exclusive = False
    if primary_skills[0][0] == '-':
        exclusive = True
        all_skills_but = []
        for skill in primary_skills:
            all_skills_but.append(re.sub(r'[-()]','', skill))
        all_skills_but.append('-1')

    def annualCounter(ex):
        ''' Updates empl_by_year dictionary '''
        if ex['identifier'] in tickers and ex['start'] != "None" and (ex['end'] != "None" or ex['current_job'] == "True"):
            empl_by_year[ex['identifier']] += Counter(
                range(
                    pd.to_datetime(ex['start']).year,
                    pd.to_datetime(ex['end']).year if ex['end']!="None" else 2019
                )
            )


    def load_and_process(line):
        entry = json.loads(line)
        profile_keys = ['year_of_birth','gender','primary_skill', 
        'secondary_skill', 'country','degrees','elite_edu']
        try:
            profile = {k:entry[k] for k in profile_keys}
        except KeyError as e:
            print(entry)
            print(e)
        #print('----profile----')
        #print(profile)

        if profile['gender'] == 'male':
            profile['gender'] = 2
        elif profile['gender'] == 'female':
            profile['gender'] = 1
        else:
            profile['gender'] = 0

        profile['degrees'] = max(profile['degrees'])
        profile['primary_skill'] = profile['primary_skill']['skill']
        
        #add profile features like this
        #remember to update varlist of main.py
        profile['faculties'] = []
        profile_keys.append('faculties')
        profile['raw_skills'] = entry['raw_skills']
        profile_keys.append('raw_skills')                

        if 'all' in primary_skills and profile['primary_skill'] != '-1':
            pass
        elif exclusive and profile['primary_skill'] not in all_skills_but:
            pass
        elif profile['primary_skill'] in primary_skills:
            pass
        else: #reset without looking at experiences
            processor.employee = Employee()
            return

        for ex in entry['experience']:
            if ex['is_edu']: # education data
                try:
                    for fac in ex['role']['faculties']:
                        if fac not in profile['faculties']:
                            profile['faculties'].append(fac)
                except TypeError as e:
                    pass # TypeError when ex['role'] = None, which we ignore
            else: #employment data
                #filter irregular workers
                if ex['role'] != None:
                    irregular_worker_filter = [re.search(r"(?i)\W{}\W".format(x)," "+ex['role']['original']+" ") 
                                            is None for x in ["intern","internship","trainee","student"]]
                    is_irregular_worker = (sum(irregular_worker_filter) !=4)
                    if is_irregular_worker:
                        continue
                    else:
                        processor.json_read(entry['user_id'], ex, profile, profile_keys)
                        annualCounter(ex)
                elif ex['identifier'] == 'TIME_OFF' : #ex[role] == None 
        
                        processor.json_read(entry['user_id'], ex, profile, profile_keys)                       

    #calling load_and_process on line
    if os.path.isdir(empl_path):
        empl_file_lst = os.listdir(empl_path)
        for empl_file_name in empl_file_lst:
            empl_file = empl_path + '/' +empl_file_name
            if infer_tickers:
                ticker = empl_file_name[:-5].upper()
                processor.change_ticker([ticker])
            with open(empl_file) as f:
                for line in f:
                    load_and_process(line)
    elif os.path.isfile(empl_path):
        with open(empl_path) as f:
            for line in f:
                load_and_process(line)