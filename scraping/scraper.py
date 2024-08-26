import os
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class JobScraper:
    def __init__(self, start_page, end_page, csv_file_path):
        self.start_page = start_page
        self.end_page = end_page
        self.csv_file_path = csv_file_path
        self.driver = webdriver.Chrome()
        self.fields = {
            'Job Title': ('.title', 'text'),
            'Company Name': ('.comp-name', 'text'),
            'Experience Required': ('.exp-wrap .expwdth', 'text'),
            'Salary': ('.sal-wrap .ni-job-tuple-icon-srp-rupee', 'text'),
            'Location': ('.loc-wrap .locWdth', 'text'),
            'Description': ('.job-desc', 'text'),
            'Skills': ('.tags-gt .tag-li', 'list'),
            'Time Posted': ('.job-post-day', 'text'),
            'Reviews': ('.review', 'text')
        }
    
    def safe_extract_text(self, element, selector, attribute='text'):
        try:
            if attribute == 'text':
                return element.find_element(By.CSS_SELECTOR, selector).text.strip()
            else:
                return element.find_element(By.CSS_SELECTOR, selector).get_attribute(attribute).strip()
        except:
            return "no data available"
    
    def scrape_page(self, page_number):
        self.driver.get(f'https://www.naukri.com/software-engineering-jobs-{page_number}?k=software+engineering')
        try:
            job_listings = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.cust-job-tuple.layout-wrapper.lay-2.sjw__tuple'))
            )
            return job_listings
        except Exception as e:
            print(f"Error extracting job listings on page {page_number}: {str(e)}")
            return []
    
    def extract_job_data(self, listing):
        job_data = {}
        for field, (selector, attr) in self.fields.items():
            if attr == 'list':
                job_data[field] = ', '.join([item.text for item in listing.find_elements(By.CSS_SELECTOR, selector)]) or "no data available"
            else:
                job_data[field] = self.safe_extract_text(listing, selector, attr)
        return job_data
    
    def run_scraping(self):
        file_exists = os.path.isfile(self.csv_file_path)
        with open(self.csv_file_path, mode='a' if file_exists else 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fields.keys())
            if not file_exists:
                writer.writeheader()
            
            for page in range(self.start_page, self.end_page):
                job_listings = self.scrape_page(page)
                print(f"Page {page}: Found {len(job_listings)} job listings")
                
                for listing in job_listings:
                    job_data = self.extract_job_data(listing)
                    writer.writerow(job_data)
        
        self.driver.quit()

csv_file_path = '../data/raw/naukri_job_listings.csv'
scraper = JobScraper(start_page=100, end_page=400, csv_file_path=csv_file_path)
scraper.run_scraping()
