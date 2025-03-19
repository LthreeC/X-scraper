import json
import os
import time
from datetime import timedelta
import random

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from common import INPUT_PATH, OUTPUT_PATH


def set_token(
        driver: webdriver.Chrome,
        token: str
) -> None:
    src = f"""
            let date = new Date();
            date.setTime(date.getTime() + (7*24*60*60*1000));
            let expires = "; expires=" + date.toUTCString();

            document.cookie = "auth_token={token}"  + expires + "; path=/";
        """
    driver.execute_script(src)


def load_conf() -> dict:
    with open(os.path.join(INPUT_PATH, "conf.json"), "r") as file:
        return json.loads(file.read())


def open_driver(
        headless: bool = False,
        agent: str = None,
) -> webdriver.Chrome:
    options = Options()
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--mute-audio')
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    options.add_argument("--disable-features=VideoPlayback")
    options.add_argument('--disable-application-cache')
    options.add_argument('--disable-cache')
    options.add_argument('--log-level=3')
    options.add_argument('--silent')

    options.page_load_strategy = 'eager'

    if headless:
        options.add_argument('--headless')
    if agent:
        options.add_argument(f"user-agent={agent}")

    driver = webdriver.Chrome(options=options)
    return driver


def count_hours(start_datetime, date, offset=0):
    known_time = date
    current_time = start_datetime - timedelta(hours=offset)
    delta = current_time - known_time
    return delta.total_seconds() / 3600


def driver_quit(driver):
    driver.close()
    driver.quit()


def save(results, name, start_time=None):
    formatted_date = start_time.strftime('%Y-%m-%d_%H-%M-%S')
    output_file_name = name + "__" + formatted_date
    os.makedirs(os.path.join(OUTPUT_PATH, name), exist_ok=True)
    output_file_path = os.path.join(OUTPUT_PATH, name, output_file_name)
    save_json = output_file_path + ".json"

    json.dump(results, open(save_json, "w", encoding='utf-8'), ensure_ascii=False, indent=4)


def split_list_per_user(task_list, users):
    num_ids = len(task_list)
    base_size = num_ids // users
    remainder = num_ids % users
    split_id_lists = []
    start_index = 0
    for i in range(users):
        sub_size = base_size + 1 if i < remainder else base_size
        if start_index + sub_size > num_ids:
            split_id_lists.append([])
        else:
            split_id_lists.append(task_list[start_index:start_index + sub_size])
        start_index += sub_size
    return split_id_lists


def get_full_page(driver, total_duration):
    last_height = driver.execute_script("return document.body.scrollHeight")
    start_time = time.time()
    while True:
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(0.1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height > last_height:
            start_time = time.time()
        last_height = new_height
        if time.time() - start_time > total_duration:
            break

    driver.execute_script("window.scrollTo(0, 0);")

def random_mouse_movement(driver, times=5):
    actions = ActionChains(driver)
    body_element = driver.find_element(By.TAG_NAME, 'body')
    for _ in range(random.randint(1, times)):
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        actions.move_to_element_with_offset(body_element, x, y).click().perform()
        time.sleep(random.uniform(0, 1))



class SafeDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._convert_nested_dicts()

    def _convert_nested_dicts(self):
        for key, value in self.items():
            if isinstance(value, dict) and not isinstance(value, SafeDict):
                super().__setitem__(key, SafeDict(value))

    def __getitem__(self, key):
        if key not in self:
            self[key] = SafeDict()
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, SafeDict):
            value = SafeDict(value)
        super().__setitem__(key, value)

    def __bool__(self):
        return bool(len(self))