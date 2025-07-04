import os
import time
import hashlib
import requests
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException

# Configuration - Focused on Multiple Ethnicities
# Configuration - Focused on European Ethnicities
ETHNICITIES = [
    "French", "German", "Italian", 
    "Spanish", "Polish", "Russian"
]
MAKEUP_TYPES = [
    "withoutMakeup", "nonmakeup",  
]

IMAGES_PER_CATEGORY = 200
OUTPUT_FOLDER = "multi_ethnic_makeup"
TARGET_SIZE = (256, 256)

# Create output folder
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Set up Chrome driver
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-logging")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-features=VoiceTranscription")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)
print("🚀 Chrome driver initialized in headless mode")

downloaded_count = 0
image_hashes = set()

def download_and_process(img_url, ethnicity, makeup_type):
    global downloaded_count
    
    try:
        response = requests.get(img_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
            "Referer": "https://www.pinterest.com/"
        }, timeout=15)
        
        if response.status_code != 200:
            return False
        
        content_hash = hashlib.md5(response.content).hexdigest()
        if content_hash in image_hashes:
            return False
        image_hashes.add(content_hash)
        
        img = Image.open(BytesIO(response.content))
        if img.width > img.height or img.width < 300:
            return False
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img = img.resize(TARGET_SIZE, Image.LANCZOS)
        
        category_folder = os.path.join(OUTPUT_FOLDER, f"{ethnicity}_{makeup_type.replace(' ', '_')}")
        os.makedirs(category_folder, exist_ok=True)
        
        filename = f"{ethnicity}_{makeup_type.replace(' ', '_')}_{downloaded_count + 1:05d}.jpg"
        img.save(os.path.join(category_folder, filename), quality=95)
        
        downloaded_count += 1
        return True
        
    except Exception:
        return False

def scrape_ethnic_makeup(ethnicity, makeup_type):
    global downloaded_count
    
    query = f"{ethnicity} women {makeup_type}"
    print(f"\n🔍 Searching for: '{query}'")
    search_url = f"https://www.pinterest.com/search/pins/?q={query.replace(' ', '%20')}"
    driver.get(search_url)
    time.sleep(3)
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    type_count = 0
    
    while type_count < IMAGES_PER_CATEGORY and scroll_attempts < 10:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
        else:
            scroll_attempts = 0
        last_height = new_height
        
        try:
            images = driver.find_elements(By.CSS_SELECTOR, "img[src*='pinimg']")
            print(f"🎨 Found {len(images)} potential images | Downloaded: {type_count}/{IMAGES_PER_CATEGORY} for {ethnicity} {makeup_type}")
            
            for img in images:
                if type_count >= IMAGES_PER_CATEGORY:
                    break
                
                try:
                    img_url = img.get_attribute("src")
                    if not img_url or "236x" not in img_url:
                        continue
                    
                    img_url = img_url.replace("236x", "564x")
                    
                    if download_and_process(img_url, ethnicity, makeup_type):
                        type_count += 1
                        print(f"✅ Downloaded: {type_count}/{IMAGES_PER_CATEGORY} for {ethnicity} {makeup_type} | Total: {downloaded_count}", end="\r")
                
                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue
        except Exception:
            continue
    
    return type_count

# Main scraping loop
try:
    total_categories = len(ETHNICITIES) * len(MAKEUP_TYPES)
    completed_categories = 0
    
    for ethnicity in ETHNICITIES:
        for makeup_type in MAKEUP_TYPES:
            completed_categories += 1
            count = scrape_ethnic_makeup(ethnicity, makeup_type)
            print(f"\n✅ Finished: {ethnicity} {makeup_type} with {count} images")
            print(f"📊 Progress: {completed_categories}/{total_categories} categories completed")
    
    print("\n✨ Scraping completed successfully!")

except Exception as e:
    print(f"\n⚠️ Critical error during scraping: {str(e)}")

finally:
    driver.quit()
    print("🛑 Chrome driver closed")

# Summary
print(f"\n📦 Total images downloaded: {downloaded_count}")
print(f"📁 Images saved in: {os.path.abspath(OUTPUT_FOLDER)}")

# Per-category report
if downloaded_count > 0:
    print("\n🗂️ Folder-wise image count:")
    for ethnicity in ETHNICITIES:
        for makeup_type in MAKEUP_TYPES:
            folder_name = f"{ethnicity}_{makeup_type.replace(' ', '_')}"
            folder_path = os.path.join(OUTPUT_FOLDER, folder_name)
            if os.path.exists(folder_path):
                count = len(os.listdir(folder_path))
                print(f"- {folder_name}: {count} images")
