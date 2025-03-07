import os
import time
import io
import pandas as pd
import requests
import zipfile
import random
import xml.etree.ElementTree as ET
import json
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from pymongo import MongoClient

# 🔧 CONFIGURATION
GECKODRIVER_PATH = r"C:/semester 4/Bigdata/Tugas1/Financial-Data-Scraper-main/geckodriver.exe"
FIREFOX_BINARY_PATH = r"C:/Program Files/Mozilla Firefox/firefox.exe"
OUTPUT_DIR = "financial_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

IDX_URL = "https://www.idx.co.id/id/perusahaan-tercatat/laporan-keuangan-dan-tahunan/"

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "IDX_Financial_Data"

# 🚀 Function to initialize WebDriver
def init_driver():
    options = Options()
    options.binary_location = FIREFOX_BINARY_PATH
    service = Service(GECKODRIVER_PATH)
    driver = webdriver.Firefox(service=service, options=options)
    return driver

# Function to download ZIP file
def download_zip(url, company_code):
    try:
        print(f"🔽 Downloading ZIP for {company_code}...")
        response = requests.get(url)
        response.raise_for_status()
        print(f"✅ ZIP downloaded successfully for {company_code}")
        return response.content
    except Exception as e:
        print(f"❌ Error downloading ZIP for {company_code}: {e}")
        return None

# Function to extract XML from ZIP
def extract_xml_from_zip(zip_content):
    try:
        print("🔓 Extracting XML from ZIP...")
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
            xml_files = [f for f in zip_file.namelist() if f.endswith('.xml')]
            if not xml_files:
                print("❌ No XML files found in ZIP")
                return None
            xml_content = zip_file.read(xml_files[0])
        print("✅ XML extracted successfully")
        return xml_content
    except Exception as e:
        print(f"❌ Error extracting XML from ZIP: {e}")
        return None

# Fungsi untuk menghapus namespace dari tag XML
def remove_namespace(tag):
    return tag.split('}')[-1] if '}' in tag else tag

# Function to convert XML to JSON (tanpa namespace)
def xml_to_json(xml_content):
    try:
        print("🔄 Converting XML to JSON...")
        root = ET.fromstring(xml_content)

        # Hapus namespace dan konversi ke dictionary
        json_data = {remove_namespace(elem.tag): elem.text for elem in root.iter()}
        
        print("✅ XML converted to JSON successfully")
        return json_data
    except Exception as e:
        print(f"❌ Error converting XML to JSON: {e}")
        return None

# Function to save data to MongoDB
def save_to_mongodb(data, company_code, year, period):
    try:
        print(f"💾 Saving data for {company_code} to MongoDB...")
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[f"{year}"]
        
        document = {
            "company_code": company_code,
            "year": year,
            "period": period,
            "data": data
        }
        
        collection.insert_one(document)
        print(f"✅ Data saved successfully for {company_code} - {year} {period}")
    except Exception as e:
        print(f"❌ Error saving data to MongoDB: {e}")

# 📄 Function to scrape financial data
def scrape_financial_data(driver):
    years = ["2021", "2022", "2023", "2024"]
    periods = ["audit"]
    download_path = os.path.expanduser("~/Downloads")

    for year in years:
        for period in periods:
            print(f"\n🌐 Scraping: Year {year}, Period {period}")
            driver.get(IDX_URL)
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print(f"✅ Page loaded for Year {year}, Period {period}")

            try:
                # Select year
                year_radio = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f"input[name='year'][value='{year}']"))
                )
                year_radio.click()
                print(f"✅ Selected year {year}")

                time.sleep(3)

                # Select period
                period_radio = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f"input[name='period'][value='{period}']"))
                )
                period_radio.click()
                print(f"✅ Selected period {period}")

                time.sleep(3)

                # Click "Terapkan" button
                apply_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn--primary"))
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", apply_button)
                time.sleep(1)
                apply_button.click()
                print("✅ Clicked 'Terapkan' button")

                # Get total number of pages
                select_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "select.form-input"))
                )
                select = Select(select_element)
                total_pages = len(select.options)

                for page in range(1, total_pages + 1):
                    print(f"\n📄 Processing page {page} of {total_pages}")

                    # Wait for the boxes to load
                    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.box")))
                    print("✅ Boxes loaded")

                    # Find all boxes
                    boxes = driver.find_elements(By.CSS_SELECTOR, "div.box")
                    
                    for box in boxes:
                        try:
                            # Extract company code from box title
                            company_code = box.find_element(By.CSS_SELECTOR, "span.f-20.f-m-30").text
                            print(f"🔍 Processing company: {company_code}")

                            # Find table rows within this box
                            rows = box.find_elements(By.CSS_SELECTOR, "table tbody tr")
                            
                            for row in rows:
                                download_links = row.find_elements(By.CSS_SELECTOR, "a.link-download")
                                
                                for link in download_links:
                                    if 'instance.zip' in link.get_attribute("href"):
                                        print(f"🔍 Found instance.zip for {company_code}")
                                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", link)
                                        time.sleep(1)
                                        link.click()
                                        print(f"✅ Clicked download for {company_code}")
                                        
                                        # Wait for download to complete
                                        time.sleep(5)
                                        
                                        # Process the downloaded file
                                        zip_file = f"instance.zip"
                                        zip_path = os.path.join(download_path, zip_file)
                                        
                                        if os.path.exists(zip_path):
                                            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                                                xml_files = [f for f in zip_ref.namelist() if f.endswith('.xbrl') or f.endswith('.xml')]
                                                if xml_files:
                                                    xml_content = zip_ref.read(xml_files[0]).decode('utf-8')
                                                    json_data = xml_to_json(xml_content)
                                                    save_to_mongodb(json_data, company_code, year, period)
                                            
                                            # Remove the zip file
                                            os.remove(zip_path)
                                            print(f"✅ Processed and removed {zip_file}")
                                        else:
                                            print(f"❌ Download failed for {company_code}")
                                        
                                        break

                        except Exception as e:
                            print(f"❌ Error processing box for {company_code}: {e}")
                            continue

                    print(f"✅ Finished processing page {page}")

                    # Move to the next page if not on the last page
                    if page < total_pages:
                        next_button = driver.find_element(By.CSS_SELECTOR, "button.btn-arrow.--next")
                        next_button.click()
                        time.sleep(3)  # Wait for the next page to load

                print(f"✅ All pages processed for {year} - {period}")

            except Exception as e:
                print(f"❌ Error processing {year} - {period}: {e}")
                continue

    print("\n🚪 All years and periods processed")

# 🔥 Main function
def main():
    driver = init_driver()

    try:
        scrape_financial_data(driver)
    finally:
        driver.quit()
        print("\n🚪 Browser closed. All scraping completed!")

# 🏁 Run the script
if __name__ == "__main__":
    main()
