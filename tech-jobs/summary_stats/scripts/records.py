import numpy as np

class Records:
    def __init__(self):
        self.data = []
    
    def output(self):
        return self.data
    
    # Three functions to output records.
    # Varlist: Hiring/Leaving/Firing, Ticker, year-month, profile_info: [...], next_industry.
    def enter_record(self, employee):
        event = ['hiring',employee.ticker,employee.start_date
               ]+employee.profile+[employee.job_role, employee.department
                              ]+['']+['',''] 
        self.data.append(event)


    def leave_record(self, employee, next_industry):
        event = ['leaving',employee.ticker,employee.end_date
               ]+employee.profile+[employee.job_role, employee.department
                              ]+[next_industry]+[time_diff(employee.end_date,employee.start_date),
                                                 employee.nth_posit]
        self.data.append(event)

    def fired_record(self, employee):
        event = ['firing',employee.ticker,employee.end_date
               ]+employee.profile+[employee.job_role, employee.department
                              ]+['']+[time_diff(employee.end_date,employee.start_date),
                                      employee.nth_posit]
        self.data.append(event)

def time_diff(end_date,start_date):
    if end_date is not None and start_date is not None:
        edt, sdt = int(end_date), int(start_date)
        yr_diff = edt//100-sdt//100
        emth = edt%100
        smth = sdt%100
        if not yr_diff and not (emth and smth):
            return min(6,(emth-smth-1)%12+1)
        else:
            return yr_diff*12+(emth if emth else 6)-(smth if smth else 6)
    else:
        return np.nan