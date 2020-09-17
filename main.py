
from link_bot import *



# example urls, indeed and careerbuilder.com
indeed_admin = "https://www.indeed.com/jobs?q=Administration&l=New%20York%20State&explvl=entry_level&vjk=40871ce8c6d1b3a5"
careers_san_fran = "https://www.careerbuilder.com/jobs?utf8=%E2%9C%93&keywords=&location=San+Francisco"
careers_receptionist = "https://www.careerbuilder.com/jobs?utf8=%E2%9C%93&keywords=receptionist&location=San+Francisco%2C+CA"
careers_medsec = "https://www.careerbuilder.com/jobs-medical-secretary"
careers_philly_admin = "https://www.careerbuilder.com/jobs-administrative-assistant-in-philadelphia,pa"
careers_boston_admin = "https://www.careerbuilder.com/jobs?utf8=%E2%9C%93&keywords=Administrative+Assistant&location=Boston%2C+MA"


def link_bot_tester():
    job = 'Office Administration'
    l = LinkBot(job_category=job, city='Philadelphia', page_number=2, link_cap=100)
    l.pull_job_links()

    l = LinkBot(job_category=job, city='Boston', page_number=2, link_cap=100)
    l.pull_job_links()


def main():
    link_bot_tester()
    #JobBot()
    #EmailBot(user=email, passw=passw)


main()