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

class EntryProcessor:    
    
    def __init__(self, employee, records):
        self.current_id = None
        self.employee = employee
        self.records = records
    
    # When id changes, record a possible leave and then clear contents.
    def reinitialize(self,entry):
        if self.employee.f_current == 'False':
            self.records.leave_record(self.employee, 'unknown') #data type of industry? 
        self.employee.reset([entry[x] for x in [1,2,3,5,8,9,10,29]], entry[6])
        self.current_id = entry[0]
    
    def change_ticker(self, ticker):
        self.ticker = ticker

###############################################################################
    # Main method: read and process.
    def read(self,entry):
        # Reinitialize when id changes.
        if self.current_id != entry[0]:
            self.reinitialize(entry)
        # Then deal with the current entry. 
        # Entry[21] contains normalized ticker
        if self.employee.ticker == entry[21] and self.employee.ticker == self.ticker:
            #The person stays in the same company
            self.employee.update(entry[13], entry[14], entry[15])
        else:
            if self.employee.ticker == self.ticker: 
                #The person leaves (or gets fired) by a company of interest
                if entry[25] == "TIME_OFF" and int(entry[16]) > 100:
                    self.records.fired_record(self.employee)
                else:
                    self.records.leave_record(self.employee, entry[25])
                # self.employee is no longer in a company of interest
                self.employee.ticker = entry[21]
                self.employee.f_current = 'false/recorded'

            if entry[21] == self.ticker: 
                #The person enters a company of interest
                self.employee.enter((entry[11], entry[12]),(entry[13], entry[14]),
                                entry[21], entry[15], entry[17], entry[18])
                self.records.enter_record(self.employee)
