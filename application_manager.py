import pandas as pd

from person_generator import *


# take links from link bot, get dataframe
# set that process as optional, or read from existing dataframe (i.e. cached links)
# a method that shoots an application for a treatment, then updates the dataframe for that treatment

class TreatmentManager:
    def __init__(self, json_file_path: str = 'input_data/treatments.json'):
        self.json_file_path = json_file_path
        self.treatment_defs = self.retrieve_treatment_definitions()
        self.current_treament = 1

    def retrieve_treatment_definitions(self):
        with open(self.json_file_path) as f:
            self.treatments = json.load(f)
            return self.treatments

    def get_next_treament(self):
        self.current_treament = (self.current_treament % 5) + 1

    def get_current_treatment_info(self):
        return self.treatment_defs['t' + str(self.current_treament)]


class ApplicationManager:
    def __init__(self, used_cached_links: bool = True, dataframe_path: str = 'job_apps.csv'):
        self.person_manager = PersonGenerator()

        # currently assuming links generated and dataframe avail, if not, can generate manually with link bot
        self.df = pd.read_csv('job_apps.csv')
        print(self.df.columns)
        print(self.df.head)
        # each job (row) should have a person generator and a treatment manager attached
        pg_map = {}
        tm_map = {}
        for index, row in self.df.iterrows():
            pg_map[index] = PersonGenerator()
            tm_map[index] = TreatmentManager()

        # deal with each treatment one at a time
        for treat in range(1, 6):
            self.df['t' + str(treat)] = ''
            for i in self.df.index:
                job_link = self.df.at[i, 'absolute_url']
                person = pg_map[i].get_person()
                # place their email into the cell, just to test the dataframe edit (TODO: fit in the application)
                self.df.at[i, 't' + str(treat)] = person.email


        print(self.df)
        self.df.to_csv(dataframe_path, index=False)


a = ApplicationManager()