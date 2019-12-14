from employee import Employee

class EntryProcessor:    
    def __init__(self, employee, records, tickers):
        self.current_id = None
        self.employee = employee
        self.records = records
        self.tickers = tickers
    
    # When id changes, record a possible leave and then clear contents.
    def reinitialize(self,entry):
        if self.employee.f_current == 'False':
            self.records.leave_record(self.employee, 'unknown') #data type of industry? 
        profile = [entry[x] for x in [1,2,3,5,8,9,10]]
        profile.append([]) # place for faculty
        profile.append([]) # placeholder for raw_skills
        self.employee = Employee(profile, entry[6])
        self.current_id = entry[0]
    
    def change_ticker(self, tickers):
        self.tickers = tickers

###############################################################################
    # Main method: read and process.
    def csv_read(self,entry):
        # Reinitialize when id changes.
        if self.current_id != entry[0]:
            self.reinitialize(entry)
        # Then deal with the current entry. 
        # Entry[21] contains normalized ticker
        if self.employee.ticker == entry[21] and self.employee.ticker in self.tickers:
            #The person stays in the same company
            self.employee.update(entry[13], entry[14], entry[15])
        else:
            if self.employee.ticker in self.tickers: 
                #The person leaves (or gets fired) by a company of interest
                if entry[25] == "TIME_OFF" and int(entry[16]) > 100:
                    self.records.fired_record(self.employee)
                else:
                    self.records.leave_record(self.employee, entry[25])
                # self.employee is no longer in a company of interest
                self.employee.ticker = entry[21]
                self.employee.f_current = 'false/recorded'

            if entry[21] in self.tickers: 
                #The person enters a company of interest
                self.employee.enter((entry[11], entry[12]),(entry[13], entry[14]),
                                entry[21], entry[15], entry[17], entry[18])
                self.records.enter_record(self.employee)

    def json_read(self, usrid, experience, profile, keys):
        if usrid != self.current_id:
            if self.employee.f_current == 'False':
                self.records.leave_record(self.employee, 'unknown') #data type of industry?
            self.current_id = usrid
            second_skill_level = profile['secondary_skill']['confidence']
            profile['secondary_skill'] = profile['secondary_skill']['skill']
            p = [profile[k] for k in keys]
            self.employee = Employee(p, second_skill_level)
        
        # Then deal with the current entry. 
        if self.employee.ticker == experience['identifier'] and self.employee.ticker in self.tickers:
            #The person stays in the same company
            self.employee.update(experience['end'], str(experience['valid_end']), str(experience['current_job']))
        else:
            if self.employee.ticker in self.tickers: 
                #The person leaves (or gets fired) by a company of interest
                if experience['identifier'] == "TIME_OFF" and int(experience['duration']) > 100:
                    self.records.fired_record(self.employee)
                else:
                    self.records.leave_record(self.employee, experience['industry'])
                # self.employee is no longer in a company of interest
                self.employee.ticker = experience['identifier']
                self.employee.f_current = 'false/recorded'

            if experience['identifier'] in self.tickers: 
                #The person enters a company of interest
                self.employee.enter((experience['start'], experience['valid_start']),(experience['end'], experience['valid_end']),
                                experience['identifier'], experience['current_job'], experience['role']['valid_roles'], experience['role']['departments'])
                self.records.enter_record(self.employee)
