import os
import time
import logging
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys


class MovieScraper:
    def __init__(self, driver, num_pages=10):
        self.driver = driver
        self.num_pages = num_pages
        self.sleep_time = random.randint(3, 7)

    def __del__(self):
        self.driver.quit()  # 确保资源被正确释放

    def navigate_to_next_page(self):
        """翻到下一页"""
        try:
            next_page_element = driver.find_element(By.CLASS_NAME, "next")
            next_page_button = next_page_element.find_element(By.TAG_NAME, "a")
            next_page_button.click()
        except (TimeoutException, NoSuchElementException, ElementNotInteractableException) as e:
            logging.error(f"无法定位到下一页元素: {e}. 当前页面URL: {self.driver.current_url}")
            raise

    # 实现电影信息爬取的方法
    def scrape_movie_info(self):
        movie_info_list = []

        for p in range(1, self.num_pages+1):
            this_page_element = self.driver.find_element("css selector", 'span.thispage')
            current_page = this_page_element.text
            logging.info(f'Start getting page {current_page}...')

            movie_info_per_page = self.get_info_by_page()
            movie_info_list.extend(movie_info_per_page)
            if int(current_page) < self.num_pages:
                self.navigate_to_next_page()

        return movie_info_list

    def get_info_by_page(self):
        li_list = self.driver.find_elements(
            By.XPATH, '//*[@id="content"]/div/div[1]/ol/li')
        logging.info(f'Start getting {len(li_list)} movies...')
        movie_details = []
        for li in li_list:
            movie_detail = {}
            try:
                url_element = li.find_element(By.XPATH, './div/div[2]/div[1]/a')
                movie_url = url_element.get_attribute("href")
                movie_title = li.find_element(
                    By.XPATH, "./div/div[2]/div[1]/a/span[1]").text

                movie_detail["url"] = movie_url
                movie_detail["title"] = movie_title

                #保存当前
                main_window_handle = driver.current_window_handle
                url_element.send_keys(Keys.CONTROL + Keys.RETURN)
                all_handles = driver.window_handles
                new_window_handle =  all_handles[2]
                driver.switch_to.window(new_window_handle)

                logging.info(f'start getting movie {movie_title}')
                self.get_movie_detail(movie_detail)
                logging.info(f'finish getting {movie_title}:\n{movie_detail}')
                movie_details.append(movie_detail)

                driver.close()
                driver.switch_to.window(main_window_handle)

            except Exception as e:
                print(e)
        return movie_details

    def get_movie_detail(self, movie_detail):
        try:
            # 使用WebDriverWait和expected_conditions来设置超时时间
            parent_ele = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/h1'))
            )
            year = parent_ele.find_element(By.XPATH, './span[2]').text

            info_ele = self.driver.find_element(By.ID, 'info')
            try:
                more_actor = info_ele.find_element(By.CLASS_NAME, 'more-actor')
                more_actor.click()
            except:
                logging.info('no more actor')
                pass
            info_text = info_ele.text
            movie_info = self._parse_info_text(info_text)

            # 获取导演、编剧等信息
            director = movie_info.get("导演")
            play_writer = movie_info.get("编剧")
            cast = movie_info.get("主演")
            movie_type = movie_info.get("类型")
            region = movie_info.get("制片国家/地区")
            language = movie_info.get("语言")
            date = movie_info.get("上映日期")
            duration = movie_info.get("片长")
            other_names = movie_info.get("又名")
            imdb_id = movie_info.get("IMDb")

            rating_ele = self.driver.find_element(By.CSS_SELECTOR, '.rating_num')

            rating = rating_ele.text

            # 获取播放网站
            sites = self._get_play_sites()

            # 获取摘要
            intro_ele = driver.find_element(By.ID, "link-report-intra")
            try:
                intro_ele.find_element(By.CLASS_NAME, "all.hidden")
                intro_ele.find_element(By.CLASS_NAME, "a_show_full").click()
                intro = intro_ele.find_element(By.CLASS_NAME, "all.hidden").text
            except:
                intro = driver.find_element(By.CSS_SELECTOR, "div#link-report-intra span[property='v:summary']").text

            # 更新movie_detail字典
            movie_detail["other_names"] = other_names
            movie_detail["director"] = director
            movie_detail["play_writer"] = play_writer
            movie_detail["cast"] = cast
            movie_detail["intro"] = intro
            movie_detail["year"] = year
            movie_detail["type"] = movie_type
            movie_detail["region"] = region
            movie_detail["date"] = date
            movie_detail["duration"] = duration
            movie_detail["imdb_id"] = imdb_id
            movie_detail["rating"] = rating
            movie_detail["websites"] = sites

        except NoSuchElementException as e:
            print(f"Element not found: {e}")

        return movie_detail

    def _parse_info_text(self, info_text):
        movie_info = {}
        info_lines = info_text.split('\n')
        for line in info_lines:
            key_value = line.split(': ', 1)
            if len(key_value) == 2:
                key, value = key_value
                movie_info[key] = value
        return movie_info

    def _get_play_sites(self):
        sites = ""
        try:
            play_buttons = driver.find_elements(By.XPATH, '// *[ @ id = "content"] / div[2] / div[2] / div[1] / ul / li')
            if play_buttons:
                sites = []
                for button in play_buttons:
                    site_name = button.find_element(By.XPATH, './a').text
                    is_free = button.find_element(By.XPATH, './span').text
                    if is_free:
                        site_name = f'{site_name}({is_free})'
                    sites.append(site_name)
                sites = ", ".join(sites)
        except NoSuchElementException:
            logging.info('no play sites')
        return sites

    def save_to_excel(self, movie_info_list, save_path, save_file):
        # 将电影信息保存到 Excel 的方法
        df = pd.DataFrame(data=movie_info_list)
        current_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_path)
        output_path = os.path.join(current_dir, save_path)
        os.makedirs(output_path, exist_ok=True)
        output_file = os.path.join(output_path, save_file)
        df.to_excel(output_file, engine="xlsxwriter", index=None)
        print(f"save file to {output_file} success")


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option("detach", True)  # 不自动关闭
    options.add_argument('--start-maximized')  # 浏览器窗口最大
    driver = webdriver.Chrome(options=options)
    return driver


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("start scrape douban top 250 movies")
    driver = create_driver()
    url = 'https://movie.douban.com/top250'
    scraper = MovieScraper(driver)
    driver.get(url)
    time.sleep(scraper.sleep_time)
    t1 = time.time()
    movie_info_list = scraper.scrape_movie_info()
    t2 = time.time()
    logging.info(f"scrape {len(movie_info_list)} movies, time cost: {t2 - t1}")
    scraper.save_to_excel(movie_info_list, save_path="data/douban", save_file="douban_top_250_detail.xlsx")
