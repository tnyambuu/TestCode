import concurrent.futures
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd


all_car_data = []
data_lock = threading.Lock()

class ScrapClass():

    def get_optimized_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-images")
        options.add_argument("--disable-javascript")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.page_load_strategy = 'eager'

        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


    def excel_writer_batch(all_car_data, batch_size=500):
        print(f"Writing {len(all_car_data)} rows in batches of {batch_size}")

        try:
            df = pd.read_excel("car_info.xlsx")
        except:
            df = pd.DataFrame(columns=['Car mark', 'Car price', 'upload time'])

        for i in range(0, len(all_car_data), batch_size):
            batch = all_car_data[i:i + batch_size]
            new_df = pd.DataFrame(batch)
            df = pd.concat([df, new_df], ignore_index=True)

            if i % (batch_size * 5) == 0:
                df.to_excel("car_info.xlsx", index=False)
                print(f"💾 Saved {len(df)} rows so far...")

        df.to_excel("car_info.xlsx", index=False)
        print(f"✅ Total rows written: {len(df)}")
        return df


    def scrape_page_fast(self, page_num):
        """Fast page scraping"""

        car_data = []
        driver = self.get_optimized_driver()

        try:
            url = f"https://www.unegui.mn/avto-mashin/-avtomashin-zarna/?page={page_num}"
            driver.get(url)

            datatable = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='list-simple__output js-list-simple__output  ']"))
            )

            car_elements = datatable.find_elements(By.XPATH, ".//div[@data-event-name='advert_click']")

            for car in car_elements:
                try:
                    car_price = car.find_element(By.XPATH, ".//a[@class='advert__content-price _not-title']")
                    car_title = car.find_element(By.XPATH, ".//a[@class='advert__content-title']")
                    time_info = car.find_element(By.XPATH, ".//div[@class='advert__content-date']")

                    car_data.append({
                        'Car mark': car_title.text,
                        'Car price': car_price.text,
                        'upload time': time_info.text
                    })
                except:
                    continue

        except Exception as e:
            print(f"❌ Page {page_num}: {e}")
        finally:
            driver.quit()

        return car_data


    def fast_scraper(self, max_pages=100, num_threads=8):
        print(f"🚀 Starting fast scraper: {max_pages} pages, {num_threads} threads")
        start_time = time.time()

        all_data = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(self.scrape_page_fast, page) for page in range(1, max_pages + 1)]

            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                page_data = future.result()
                if page_data:
                    all_data.extend(page_data)

                if (i + 1) % 10 == 0:
                    print(f"�� Processed {i + 1}/{max_pages} pages, collected {len(all_data)} cars")

        if all_data:
            self.excel_writer_batch(all_data)

        end_time = time.time()
        print(f"⏱️ Total time: {end_time - start_time:.2f} seconds")
        print(f"📈 Speed: {len(all_data) / (end_time - start_time):.2f} cars/second")


    def run_scraper(self):

        SCRAP_URL = "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/"
        driver = self.get_optimized_driver()

        driver.get(SCRAP_URL)
        ul_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//ul[@class='number-list']"))
        )

        last_page = None

        try :
            li_elements = ul_element.find_elements(By.XPATH, ".//li[last()]")
            last_page = int(li_elements[0].text)
        except Exception as e:
            print('last element not found: ', e)

        driver.quit()

        self.fast_scraper(max_pages=last_page, num_threads=6)


if __name__ == "__main__":
    scraper = ScrapClass()
    scraper.run_scraper()