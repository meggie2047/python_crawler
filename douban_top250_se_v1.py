import os
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By



def sleep_time():
    return random.randint(3, 7)


def get_movie_info():
    li_list = driver.find_elements(
        By.XPATH, '//*[@id="content"]/div/div[1]/ol/li')
    page_movie_urls = []
    page_movie_titles = []
    for li in li_list:
        try:
            url_element = li.find_element(By.XPATH, './div/div[2]/div[1]/a')
            movie_url = url_element.get_attribute("href")
            movie_title = li.find_element(
                By.XPATH, "./div/div[2]/div[1]/a/span[1]")
            page_movie_urls.append(movie_url)
            page_movie_titles.append(movie_title.text)

        except Exception as e:
            print(e)
    return page_movie_urls, page_movie_titles


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option("detach", True)  # 不自动关闭
    options.add_argument('--start-maximized')  # 浏览器窗口最大化
    driver = webdriver.Chrome(options=options)
    return driver


if __name__ == "__main__":
    driver = create_driver()
    url = 'https://movie.douban.com/top250'
    driver.get(url)
    time.sleep(sleep_time())

    movie_urls = []
    movie_titles = []
    for i in range(10):
        if i > 1:
            next_page = driver.find_element(
                By.XPATH, '//*[@id="content"]/div/div[1]/div[2]/span[3]/a')
            next_page.click()
            time.sleep(sleep_time())
        print(f'start get page{i+1}...')
        urls, titles = get_movie_info()
        movie_urls += urls
        movie_titles += titles

    movie_dict = {"title": movie_titles, "url": movie_urls}
    df = pd.DataFrame(data=movie_dict, columns=["title", "url"])
    current_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_path)
    output_path = os.path.join(current_dir, "data/douban")
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, "douban_top_250_info.xlsx")
    df.to_excel(output_file, engine="xlsxwriter", index=None)
    print(f"save file to {output_file} success")
