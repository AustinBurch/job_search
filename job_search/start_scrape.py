import csv
import pandas as pd
from operator import itemgetter
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains as AC
from time import sleep
import re

job_list = []
num_jobs = []

def start_browser(url):
    
    options = webdriver.ChromeOptions()
    options.add_argument('--incognito')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins-discovery')
    driver = 'C:\\Users\\austi\\Python_Programs\\chromedriver.exe'
    browser = webdriver.Chrome(driver, chrome_options=options)
    browser.get(url)

    return browser


# Start search at home page then filter job listings
def start_search(browser, job, location):
        try:
            keyword_elem = browser.find_element_by_name("sc.keyword")
            sleep(3)
            keyword_elem.send_keys(job)
            keyword_elem.send_keys(Keys.TAB)
            location_elem = browser.find_element(by=By.ID, value='LocationSearch')
            location_elem.clear()
            if not location_elem.is_displayed():
                try:
                    location_elem = browser.find_elements(By.CLASS_NAME, 'loc')
                    location_elem.clear()
                except:
                    print('Not Found')
            sleep(3)
            location_elem.send_keys(location)
            search_elem = browser.find_element_by_class_name("gd-btn-mkt")
            search_elem.click()

            #Apply Job Filter
            apply_filter(browser)
            sleep(8)
            
            #Iterate over 5 pages of jobs on site
            for page_num in range(5):
                job_num = len(num_jobs)
                jobs = parse_html(browser.page_source, job_num)
                page_num = browser.find_element(By.CLASS_NAME, 'next')
                page_num.click()
                sleep(3)
                try:
                    email_form = browser.find_element_by_xpath('//*[@id="JAModal"]/div/div[2]')
                    if email_form.is_displayed:
                        escape = browser.find_element_by_xpath('//*[@id="JAModal"]/div/div[2]/div[1]')
                        AC(browser).move_to_element(email_form).click(escape).perform()
                except:
                    print('', end='')
        except:
            print('Element not found')
        
        return jobs


            
# Apply 4 Star filter in search results
def apply_filter(browser):

    try:
    #Find more in the filter menu, perform ActionChain and click
        filter_menu = browser.find_element_by_css_selector('#DKFilters div.selectContainer .filter')
        more_elem = browser.find_element_by_css_selector('#DKFilters .more')
        AC(browser).move_to_element(filter_menu).click(more_elem).perform()


    #Find 'All Company Ratings', click 4 stars then apply
        flyout_menu = browser.find_element_by_css_selector('.moreFlyout .header .label')
        comp_rate = browser.find_element_by_xpath('//*[text()[contains(.,"All Company Ratings")]]')
        AC(browser).move_to_element(flyout_menu).click(comp_rate).perform()

        stars = browser.find_element_by_xpath('//*[@id="DKFilters"]/div/div/div[5]/div/div[4]/span[1]/i[4]/i')
        stars.click()
        apply_btn = browser.find_element_by_xpath('//*[@id="DKFilters"]/div/div/div[5]/div/div[1]/button')
        apply_btn.click()
    except:
        print('Filter element not found')


# Write Results to CSV file
def write_to_file(job_list, filename):
    with open(filename, 'a', errors='ignore') as csvfile:
        fieldnames = ['Job Number', 'Title', 'Company', 'Location', 'URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for row in job_list:
            writer.writerow(row)
        

# Parse current page and add job data to job_list dictionary
def parse_html(html, job_num):
    
    base_url = 'https://www.glassdoor.com'
    soup = BeautifulSoup(html, 'html.parser')
    job_titles = soup.find_all('div', attrs={'class':'flexbox jobTitle'})
    for a in job_titles:
        try:
            next_listing = a.findNext('a',attrs={'class' : 'jobLink'})
            title = next_listing.text
            list_url = next_listing['href']

            company_listing = a.findNext('div', attrs={'class' : 'flexbox empLoc'})
            next_company = company_listing.findNext('div')
            company = next_company.text
            company = company.replace(u'\xa0','').strip()
            company = company.replace(u'\n\n\n\n','').strip()
            
            job_num += 1
            num_jobs.append(job_num)
            
        except:
            print("Error can't find job listing")

        # Convert company to string then split and make new key/value 'Location'    
        try:
            company = str(company)
            company, location = company.split('–')    
        except:
            print("Can't change company string")
        
        # Add job data to job_list 
        job_info = {
                'Job Number' : job_num,
                'Title' : title,
                'Company' : company,
                'Location' : location,
                'URL' : base_url + list_url
            }
        
        job_list.append(job_info)
        
    return job_list
