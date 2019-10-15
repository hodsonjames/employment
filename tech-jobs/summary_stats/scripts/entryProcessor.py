import re
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import unicodecsv as csv
import seaborn as sns
from collections import Counter
from cycler import cycler
from textwrap import wrap

class entryProcessor:    
    
    def __init__(self, employee, records, ticker = None):
        self.current_id = None
        self.ticker = ticker
        self.employee = employee
        self.records = records
    
    # When id changes, record a possible leave and then clear contents.
    def reinitialize(self,entry):
        if employee.f_current == 'False':
            records.leave_record('unknown') #data type of industry? 
        employee.reset([entry[x] for x in [1,2,3,5,8,9,10]])
        self.current_id = entry[0]
        # TODO: Let emplyee do this by itself
        if entry[6] is not None and float(entry[6])<0.1:
            employee.profile[3] = ''

###############################################################################
    # Main method: read and process.
    def read(self,entry):
        # Reinitialize when id changes.
        if self.person_id != entry[0]:
            self.reinitialize(entry)
        # Then deal with the current entry. Entry21 contains normalized ticker
        if employee.ticker != entry[21]:
            if self.employment[2] in ['D','P']: # this is when the person leaves (or get fired) by the company
                if entry[25] == "TIME_OFF" and int(entry[16]) > 100:
                    records.fired_record()
                else:
                    records.leave_record(entry[25])
            self.employment = [None]*7
            if entry[21] in ['D','P']: #This is when person enters D or P from other company
                self.employment[0] = entryProcessor.convert_time(entry[11],entry[12])
                self.employment[1] = entryProcessor.convert_time(entry[13],entry[14])
                self.employment[2] = entry[21]
                self.employment[3] = entry[15]
                self.employment[4] = entry[17]
                self.employment[5] = entry[18]
                self.employment[6] = 0
                records.enter_record()
        else:
            # updating the end date, f_current, and number of promotions(repeated emplyoments)
            self.employment[1] = entryProcessor.convert_time(entry[13],entry[14]) 
            self.employment[3] = entry[15]
            self.employment[6] += 1
        
    # For print.
    def __str__(self):
        return "[person_id: {}, profile: {}, employment: {}]".format(self.person_id, self.profile, self.employment)
