from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import csv
import os
from pymongo import MongoClient
import re

# Koneksi ke MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["Berita"]
collection = db["Artikel"]


# URL awal
base_url = "http://www.iqplus.info"
start_url = base_url + "/news/stock_news/go-to-page,1.html"

# Konfigurasi Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Jalankan tanpa tampilan browser
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Inisialisasi WebDriver otomatis dengan WebDriverManager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 10)

# Fungsi untuk mendapatkan halaman terakhir
def get_last_page():
    driver.get(start_url)
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "nav")))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        nav_span = soup.find("span", class_="nav")
        
        if nav_span:
            last_page_link = nav_span.find_all("a")[-2]
            if last_page_link and last_page_link.text.isdigit():
                return int(last_page_link.text)
    except Exception as e:
        print(f"Error mendapatkan halaman terakhir: {e}")
    return 1

# Fungsi untuk mengambil konten artikel
def scrape_article_content(article_url):
    full_url = base_url + article_url if not article_url.startswith("http") else article_url
    try:
        driver.get(full_url)
        wait.until(EC.presence_of_element_located((By.ID, "zoomthis")))
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        zoom_div = soup.find("div", id="zoomthis")
        if not zoom_div:
            print(f"Konten artikel tidak ditemukan di {full_url}")
            return None, None
        
        date_element = zoom_div.find("small")
        date_text = date_element.text.strip() if date_element else "Tanggal tidak tersedia"
        
        if date_element:
            date_element.extract()
        
        title_element = zoom_div.find("h3")
        if title_element:
            title_element.extract()
        
        zoom_control = zoom_div.find("div", attrs={"align": "right"})
        if zoom_control:
            zoom_control.extract()
        
        content = zoom_div.get_text(strip=True)
        content = re.sub(r'\s+', ' ', content).strip()
        
        return date_text, content
    except Exception as e:
        print(f"Error saat scraping artikel {full_url}: {e}")
        return None, None

# Fungsi untuk mengambil berita dari satu halaman
def scrape_page(url):
    driver.get(url)
    try:
        wait.until(EC.presence_of_element_located((By.ID, "load_news")))
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        news_list = soup.select_one("#load_news .box ul.news")
        if not news_list:
            print("Elemen berita tidak ditemukan.")
            return
        
        news_items = news_list.find_all("li")
        
        for index, item in enumerate(news_items):
            time_text = item.find("b").text.strip() if item.find("b") else "Tidak ada waktu"
            title_tag = item.find("a")
            
            if title_tag and title_tag.has_attr("href"):
                title = title_tag.text.strip()
                link = title_tag["href"]
                full_link = base_url + link if not link.startswith("http") else link
                
               
                article_date, article_content = scrape_article_content(link)
                
                if not collection.find_one({"judul": title}):
                    article_data = {
                        "judul": title, 
                        "waktu": time_text, 
                        "link": full_link,
                        "tanggal_artikel": article_date,
                        "konten": article_content
                    }
                    collection.insert_one(article_data)
                
                    
                    time.sleep(1)
    except Exception as e:
        print(f"Error saat scraping {url}: {e}")

# Dapatkan halaman terakhir
last_page = get_last_page()
print(f"Halaman terakhir: {last_page}")

# Loop untuk mengambil semua halaman
for page in range(0, last_page + 1):
    page_url = f"http://www.iqplus.info/news/stock_news/go-to-page,{page}.html"
    print(f"Scraping halaman: {page_url}")
    scrape_page(page_url)

# Tutup browser Selenium
driver.quit()
print("✅ Scraping selesai.")