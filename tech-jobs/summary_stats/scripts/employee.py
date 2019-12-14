import re

class Employee:
    def __init__(self, profile = [], skill2_weight = None):
        self.profile = profile # "birth_year","gender","skill1","skill2","country","education_level","f_elite, edu_faculty", raw_skills
        self.start_date = None
        self.end_date = None
        self.ticker = None
        self.f_current = None
        self.job_role = None
        self.department = None
        self.nth_posit = None
        if skill2_weight is not None and float(skill2_weight)<0.1:
            self.profile[3] = ''
    
    def enter(self, start, end, ticker, f_current, job_role, department):
        self.start_date = convert_time(start[0], start[1])
        self.end_date = convert_time(end[0], end[1])
        self.ticker = ticker
        self.f_current = f_current
        self.job_role = job_role
        self.department = department
        self.nth_posit = 0

    # updating the end date, f_current, and number of promotions(repeated emplyoments)
    def update(self, date, f_valid_month, f_current):
        self.end_date = convert_time(date, f_valid_month)
        self.nth_posit += 1
        self.f_current = f_current

def convert_time(date,f_valid_month):
    date_regex = re.match(r"(\d{4})-(\d{2})-\d{2}",date)
    if date_regex is None:
        return None
        #raise ValueError('Not a proper date: {}'.format(date))
    else:
        return date_regex.group(1)+('00' if f_valid_month == 'False' else date_regex.group(2))