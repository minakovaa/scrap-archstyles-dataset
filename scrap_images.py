# thx Anand Suresh for some code https://medium.com/@wwwanandsuresh/web-scraping-images-from-google-9084545808a2

from selenium import webdriver
import selenium.common.exceptions as selenium_exceptions
import time
import os
from PIL import Image
import io
import hashlib
import random
import typing as tp
from dataclasses import dataclass
import aiohttp
import asyncio

# Put the path for your ChromeDriver here  for example '/usr/bin/chromedriver'
DRIVER_PATH = os.path.join(os.getcwd(), 'chromedriver')


@dataclass()
class SearchEngine:
    url: str
    css_selector_search_line: str
    css_selector_thumbnail_img: str
    css_selector_image_url: str
    close_preview: str
    prefix_to_saving_img: str


YANDEX_IMG = SearchEngine(url='https://yandex.ru/images/',
                          css_selector_search_line='input.input__control',
                          css_selector_thumbnail_img='a.serp-item__link',
                          css_selector_image_url='img.MMImage-Origin',
                          close_preview='div.MMViewerModal-Close',
                          prefix_to_saving_img='ya_')

GOOGLE_IMG = SearchEngine(url='https://www.google.com/imghp?hl=EN',
                          css_selector_search_line='input.gLFyf',
                          css_selector_thumbnail_img='img.Q4LuWd',
                          css_selector_image_url='img.n3VNCb',
                          close_preview='polygon.FAnDdb',
                          prefix_to_saving_img='go_')


def scroll_to_end(driver: webdriver, time_sleep: int = 1):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(time_sleep)


def fetch_image_urls(search_engine: SearchEngine,
                     query: str,
                     max_img_to_fetch: int,
                     driver: webdriver):
    try:
        driver.get(search_engine.url)
        search_box = driver.find_element_by_css_selector(search_engine.css_selector_search_line)
        search_box.send_keys(query)
        search_box.submit()
    except Exception as ex:
        driver.quit()
        print(f"Exception {ex} with search box.")
        return None

    image_urls = []
    image_count = 0
    results_start = 0
    while image_count < max_img_to_fetch:
        scroll_to_end(driver, time_sleep=random.randint(1, 3))

        # get all image thumbnail results
        thumbnail_results = driver.find_elements_by_css_selector(search_engine.css_selector_thumbnail_img)
        number_results = len(thumbnail_results)

        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(random.randint(1, 3))
            except Exception:
                continue

            # extract image urls
            actual_images = driver.find_elements_by_css_selector(search_engine.css_selector_image_url)
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.append(actual_image.get_attribute('src'))
                    break

            try:
                close_preview = driver.find_element_by_css_selector(search_engine.close_preview)
                close_preview.click()
            except selenium_exceptions.ElementNotVisibleException as ex:
                print(ex)
                continue
            except Exception as ex:
                print(f'Error with close_preview: {ex}')
                return image_urls

            image_count = len(image_urls)

            if len(image_urls) >= max_img_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(random.randint(10, 30))

            if search_engine is GOOGLE_IMG:
                load_more_button = driver.find_element_by_css_selector(".mye4qd")
                if load_more_button:
                    driver.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls


async def download_image_by_url(session: aiohttp.ClientSession,
                                folder_path: str,
                                url: str,
                                file_name: str = ''):
    image_content = b''
    try:
        async with session.get(url, verify_ssl=False) as resp:
            image_content = await resp.read()
    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        if not file_name or os.path.exists(file_name):
            file_name = hashlib.sha1(image_content).hexdigest()[:10] + '.jpg'

        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        file_path = os.path.join(folder_path, file_name)

        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")


def init_chrome_driver(is_headless: bool = True) -> tp.Optional['webdriver']:
    driver_op = webdriver.ChromeOptions()
    if is_headless:
        driver_op.add_argument('--headless')

    driver_op.add_argument("--window-size=800,600")  # 1920,1080
    driver_op.add_argument('--disable-gpu')
    driver_op.add_argument("--disable-extensions")

    try:
        driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=driver_op)
    except BaseException as ex:
        print(f'Cannot start webdriver. Exception {ex}')
        raise ex

    return driver


async def download_img_by_search_query(queries: tp.List[str],
                                       number_of_each_query: int,
                                       images_folder_path: str,
                                       search_engine: SearchEngine,
                                       is_headless: bool = True,
                                       subfolders_for_queries: tp.List[str] = []):

    driver = init_chrome_driver(is_headless=is_headless)

    if not subfolders_for_queries or len(subfolders_for_queries) != len(queries):
        subfolders_for_queries = queries

    async with aiohttp.ClientSession() as session:
        for query, subfolder in zip(queries, subfolders_for_queries):
            links = fetch_image_urls(search_engine, query, number_of_each_query, driver)

            if links:
                counter = 0
                for img_url in links:
                    folder_path = images_folder_path + '/' + subfolder

                    counter = counter + 1
                    str_counter = str(counter).zfill(5)
                    filename_path_to_save = search_engine.prefix_to_saving_img + str_counter + '.jpg'

                    # If this file exits generate next filename
                    while os.path.exists(os.path.join(folder_path, filename_path_to_save)):
                        counter = counter + 1
                        str_counter = str(counter).zfill(5)
                        filename_path_to_save = search_engine.prefix_to_saving_img + str_counter + '.jpg'

                    try:
                        await download_image_by_url(session=session,
                                                    folder_path=folder_path,
                                                    url=img_url,
                                                    file_name=search_engine.prefix_to_saving_img + str_counter + '.jpg')
                    except selenium_exceptions.WebDriverException as ex:
                        print(ex)
                        driver.quit()

    driver.quit()


if __name__ == '__main__':

    # Enter your path where you would like to save images
    images_path = os.path.join(os.getcwd(), 'scrap-arch')

    # Change your list of querries here
    queries = ['модерн', 'модернизм -модерн', 'хайтек', 'классицизм', 'неоготика', 'неоренессанс']
    queries = ['архитектура москва {0}'.format(query) for query in queries]

    # You must define subfolders for each query
    subfolders_for_queries = [q.split()[2] for q in queries]

    # Enter number of img of each query would you like
    number_of_each_query = 100

    for search_engine in [YANDEX_IMG, GOOGLE_IMG]:
        asyncio.run(download_img_by_search_query(queries, number_of_each_query, images_path,
                                                 search_engine=search_engine,
                                                 is_headless=False,
                                                 subfolders_for_queries=subfolders_for_queries)
                    )
