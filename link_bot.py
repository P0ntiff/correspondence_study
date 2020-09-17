from selenium import webdriver

import os.path

# to sleep
import time

from csv import DictWriter


TEST_CRITERIA = {
    "position": "receptionist",
    "location": "San Francisco"
}

MOCK_FORM_DATA = {
    "firstname": "Robert",
    "lastname": "Smith",
    "email": "rjsmith31415@gmail.com",
    "resumefile": "/home/ben/MEGA/Projects/correspondence_study/Bob_Smith_CV.pdf"
}

BASE_CAREERS_URL = "https://www.careerbuilder.com/jobs"
BLACK_LIST_KEYWORDS = ['Robert Half', 'Beacon Hill']
DATAFRAME_HEADERS = ['job_category', 'location', 'title', 'absolute_url', 'easy_apply_url', 'position_info', 'job_id']

# TODO Meeting 24/08
# 1/ Finish backend upgrade - support job and location high level inputs, support 
# 2/ Take over CV script for random field generation from excel sheet
# 3/ Check treatment ID - come up with identifier
# 4/ Setup mail server + domain for multiple email addresses


class LinkBot:
    def __init__(self, job_category: str, city: str, link_cap: int,
                 base_url: str = BASE_CAREERS_URL, page_number: int = 1):
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1280, 1000)
        # where to look
        self.base_url = base_url
        self.job_category = job_category
        self.city = city
        self.page_number = page_number
        # how many to pull (cap)
        self.link_cap = link_cap

    def generate_url(self):
        """Builds a CareerBuilder URL with params passed directly from class variables (title, city, page_number)
         eg: https://www.careerbuilder.com/jobs?keywords=Administrative+Assistant&location=Boston%2C+MA&page_number=2
        """
        result_url = self.base_url + '?keywords='
        # job title
        result_url += '+'.join(self.job_category.split(' '))
        # location
        result_url += '&location=' + self.city
        # page number
        result_url += '&page_number=' + str(self.page_number)

        return result_url

    def pull_job_links(self):
        """Gets the absolute link for each job on a page, with meta data (i.e. city / title / company), and then
           appends the data to a CSV file. Returns a list of dictionaries, one dictionary capturing the data for one job.
        """
        # result set = list of dictionaries
        data_map = []
        link_count = 0
        while link_count < self.link_cap:
            # open site
            self.driver.get(self.generate_url())
            self.driver.implicitly_wait(5)
            # filter for easy apply, apply blacklist
            ease_filter = self.driver.find_element_by_xpath("//*[@id='jobs-filters-content']/div[5]").click()
            time.sleep(3)
            # parse for job links
            job_boxes = self.driver.find_elements_by_class_name('data-results-content.block.job-listing-item')
            for job_box in job_boxes:
                # get metadata of company, location and position type (full-time/casual)
                job_info = {'location': self.city,
                            'job_category': self.job_category,
                            'position_info': job_box.find_elements_by_xpath('.//div[@class="data-details"]')[0].text,
                            'absolute_url': job_box.get_attribute('href'),
                            'job_id': job_box.get_attribute('data-job-did'),
                            'title': job_box.find_element_by_class_name('data-results-title').text}
                data_map.append(job_info)

                link_count += 1
            # go to next page (load more jobs)
            self.page_number += 1

        # filter for blacklist recruitment agencies / spam
        self.apply_blacklist(data_map)
        # get the easy apply links for each job
        self.pull_easy_apply_links(data_map)

        # output to CSV
        self.output_to_csv(data_map)

        # apply (TODO: TEMP stored in LinkBot)
        self.apply_to_easy_links(data_map)

        return data_map

    def apply_blacklist(self, data_map):
        filtered_data_map = []
        for job in data_map:
            if not any(bad_company.lower() in job['position_info'].lower() for bad_company in BLACK_LIST_KEYWORDS):
                filtered_data_map.append(job)
        return filtered_data_map

    def pull_easy_apply_links(self, data_map):
        # iterates through absolute links prev. stored in data_map
        for job in data_map:
            url = job['absolute_url']
            easy_apply_links = []
            # take listing to active view
            self.driver.get(url)
            self.driver.implicitly_wait(1)
            try:
                # try easy apply (bit of a hack, to replace later)
                #easy_apply_el = self.driver.find_element_by_class_name('btn btn-linear btn-linear-green btn-block internal-apply-cta')
                easy_apply_el = self.driver.find_element_by_xpath("//*[@id='hide-fixed-top']/a")
                ease_link = easy_apply_el.get_attribute('href')
                easy_apply_links.append(ease_link)
                job['easy_apply_url'] = ease_link
            except Exception as e:
                print('no easy apply link for {}'.format(url))

    def apply_to_easy_links(self, data_map):
        # got the easy apply links, now apply to each one (easy apply window)
        for job in data_map:
            self.driver.get(job['easy_apply_url'])
            time.sleep(2)
            self.driver.implicitly_wait(5)
            self.apply_on_easy_apply_page()

    def apply_on_easy_apply_page(self):
        # example = 'https://www.careerbuilder.com/apply/j3n6cx678590cx7fknw?ipath=CRJR2&notify=true&siteid=cbnsv'
        css_ids = ['firstname', 'lastname', 'email']
        # check if job requirements radio button is there
        try:
            radio_btn = self.driver.find_element_by_xpath('.//ul[@class="field yes-no-radio"]/li[2]')
            time.sleep(0.5)
            radio_btn.click()
        except Exception:
            pass
        try:
            for field in css_ids:
                # css_field = self.driver.find_element_by_id(field)
                css_field = self.driver.find_element_by_xpath("//*[@id='{}']".format(field))
                time.sleep(0.5)
                css_field.clear()
                time.sleep(0.5)
                css_field.click()
                time.sleep(0.5)
                css_field.send_keys(MOCK_FORM_DATA[field])
                time.sleep(0.5)

            # upload CV
            dropdown = self.driver.find_element_by_id('resume-name')
            dropdown.click()
            time.sleep(0.5)
            # 'click the file upload input
            self.driver.find_element_by_name('upload_file').send_keys(os.getcwd() + "/test_data/" + self.city
                                                                      + "/Bob_Smith_CV.pdf")
            # hit submit
            submit_btn = self.driver.find_element_by_id('submit-resume-upload-dropdown')
            submit_btn.click()
        except Exception:
            print('Could not submit application')
        time.sleep(1)

    def output_to_csv(self, data_map):
        with open('job_apps.csv', 'a+', newline='') as fd:
            # Create a writer obj from CSV module
            dict_writer = DictWriter(fd, fieldnames=DATAFRAME_HEADERS)
            for row in data_map:
                dict_writer.writerow(row)


def selenium_tester():
    # from Google minimal working example
    # Optional argument, if not specified will search path.
    driver = webdriver.Chrome('/usr/bin/chromedriver')
    # or '/usr/lib/chromium-browser/chromedriver' if you use chromium-chromedriver
    driver.get('http://www.google.com/xhtml')
    time.sleep(5)  # Let the user actually see something!
    search_box = driver.find_element_by_name('q')
    search_box.send_keys('ChromeDriver')
    search_box.submit()
    time.sleep(5)  # Let the user actually see something!
    driver.quit()