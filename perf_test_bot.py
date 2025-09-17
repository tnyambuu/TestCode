from multiprocessing import process
from typing import Self
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import os


class PerformanceTestBot():

    def __init__(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-notifications")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        # self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.file_list = []

    def login_system(self):
        try:
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            username_field.send_keys("admin@email.mn")

            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_field.send_keys("secure_password")

            btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.TAG_NAME, "button"))
            )
            btn.click()

        except Exception as e:
            print(f"Login failed: {e}")
            print("Current page URL:", self.driver.current_url)
            print("Page title:", self.driver.title)
            raise

    def open_modal(self):

        try:
            upload_btn = WebDriverWait(self.driver, 100).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-slot='tooltip-trigger']"))
            )
            upload_btn.click()

        except:
            print("error click add btn")

    def excel_writer(self, total_time, parser_name, tran_num):

        try:
            df = pd.read_excel("output.xlsx")
        except:
            print("No output file")
            df = pd.DataFrame(columns=['Parser name', '1000', '2000', '3000', '4000', '5000', '10000', '20000', '30000'])

        existing_row = None

        for idx, row in df.iterrows():
            if row.get('Parser name') == parser_name:
                existing_row = idx
                break

        if existing_row is not None:
            df.at[existing_row, tran_num] = total_time
            print(f"Updated row for {parser_name} - {tran_num}: {total_time}")

        else:
            # Add new row
            new_row = {'Parser name': parser_name}
            new_row[tran_num] = total_time
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            print(f"Added new row for {parser_name} - {tran_num}: {total_time}")

        try:
            df.to_excel("output.xlsx", index=False)
            df.to_excel("output_watch.xlsx", index=False)

        except:
            pass

    def upload_file(self, file, file_type):

        # Try multiple selector strategies for the button
        try:
            btns = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='flex gap-1']"))
            )

            btns_list = btns.find_elements(By.XPATH, ".//div[@data-slot='form-item']")

            for idx, element in enumerate(btns_list):
                if (idx == len(btns_list) - 1):
                    continue

                btn = element.find_element(By.XPATH, ".//button[@data-slot='form-control']")
                btn.click()

                btn_value = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@role='option']"))
                )


                btn_value.click()

            input = WebDriverWait(btns, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@data-slot='form-control']"))
            )
            input.send_keys("11111111")
            input_file = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='file']"))
            )

            file_input = "\n".join(file['upload_files'])
            input_file.send_keys(file_input)
            time.sleep(1)

            submit_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )

            start_time = time.perf_counter()
            submit_btn.click()

            try:
                while True:
                    try:
                        modal = self.driver.find_element(By.XPATH, "//div[@role='alertdialog']")
                        if not modal.is_displayed():
                            print("Modal disappeared.")
                            break

                    except:
                        print("Modal removed from DOM.")
                        break

            except KeyboardInterrupt:
                print("Stopped manually.")

            end_time = time.perf_counter()

            total_time = round(end_time - start_time, 1)
            print("upload time:", total_time)

            self.excel_writer(total_time, file['parser_name'] + '_' + file_type, file['tran_num'])

        except Exception as e:
            print("str_btn error: ", e)

    def file_folder(self):

        os.chdir('stress_test')
        parser_type_list = os.listdir()

        for parser_type in parser_type_list:
            parser_type_dict = {
                'parser_type': parser_type,
                'parsers': []
            }
            os.chdir(parser_type)
            parser_list = os.listdir()

            for parser in parser_list:
                parser_dict = {
                    'parser': parser,
                    'test_num': []
                }
                os.chdir(parser)
                tran_num_list = os.listdir()
                int_list = []

                for tran_num in tran_num_list:
                    try:
                        int_list.append(int(tran_num))

                    except:
                        pass

                int_list.sort()
                tran_num_list = [str(num) for num in int_list]

                for tran_num in tran_num_list:
                    tran_num_dict = {
                        'tran_num': tran_num,
                        'upload_files': [],
                        'parser_name': parser
                    }
                    os.chdir(tran_num)
                    file_list = os.listdir()
                    file_path = os.getcwd()

                    for file in file_list:
                        tran_num_dict['upload_files'].append(str(file_path + '\\' + file))

                    os.chdir('..')
                    parser_dict['test_num'].append(tran_num_dict)

                os.chdir('..')
                parser_type_dict['parsers'].append(parser_dict)

            os.chdir('..')
            self.file_list.append(parser_type_dict)

        os.chdir('..')

    def test(self):

        self.driver.get("http://localhost:3000/")
        self.file_folder()
        self.login_system()

        for file_type in self.file_list:
            for parsers in file_type['parsers']:
                for test in parsers['test_num']:

                    if test['tran_num'] == '30000' and parsers['parser'] == 'xacbank_25':
                        print(test)

                        if len(test['upload_files']) != 0:
                            self.open_modal()
                            self.upload_file(test, file_type['parser_type'])
                        else:
                            self.excel_writer(0, test['parser_name'] + '_' + file_type['parser_type'], test['tran_num'])

        input("Click Enter\n")

        self.driver.quit()

if ("__main__"):
    bot = PerformanceTestBot()
    bot.test()
    # bot.excel_writer(10, 'khanbank_3')
    # bot.excel_writer(10, 'khanbank_3')
    # bot.excel_writer(10, 'TDB')
    # bot.excel_writer(10, 'TDB')