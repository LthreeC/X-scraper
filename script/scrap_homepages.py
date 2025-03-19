import argparse
import concurrent
import time
import json
from datetime import datetime

from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from concurrent.futures import ThreadPoolExecutor

from common import get_logger
from common.utils import load_conf, set_token, open_driver, driver_quit, split_list_per_user, save, random_mouse_movement, SafeDict

logger = get_logger("global")
conf = load_conf()
COUNT = 0


def run_homepages(config):
    global COUNT
    logger.info(config)
    result = {}

    driver = open_driver(conf["headless"], conf["userAgent"][config["id"] % len(conf["userAgent"])])
    logger.info(f"user {config['id']}----{conf['token'][config['id']]} starts")

    driver.get("https://twitter.com/")
    set_token(driver, conf["token"][config["id"]])

    for ID in config["id_list"]:
        driver.get("https://twitter.com/" + ID)
        wrong_time = 0
        while True:
            data = {}
            try:
                info = WebDriverWait(driver, 4, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, "//script[@data-testid='UserProfileSchema-test']"))
                )
                info = info.get_attribute("innerText")

                json_data = json.loads(info)
                json_data = SafeDict(json_data)

                ID = json_data["mainEntity"]["additionalName"]
                Nickname = json_data["mainEntity"]["givenName"]
                Description = json_data["mainEntity"]["description"]
                dateCreated = datetime.strptime(json_data["dateCreated"], "%Y-%m-%dT%H:%M:%S.%fZ")
                dateCreated = dateCreated.strftime("%Y-%m-%d %H:%M:%S")
                homeLocation = json_data["mainEntity"]["homeLocation"]["name"]
                follower = json_data["mainEntity"]["interactionStatistic"][0]["userInteractionCount"]
                following = json_data["mainEntity"]["interactionStatistic"][1]["userInteractionCount"]
                posts = json_data["mainEntity"]["interactionStatistic"][2]["userInteractionCount"]

            except Exception as e:
                try:
                    logger.error("Waiting")
                    retry_flag = driver.find_element(By.XPATH, "//span[text()='Something went wrong. Try reloading.']")
                    time.sleep(20)
                    retry_flag.click()
                    random_mouse_movement(driver, times=30)
                    retry_flag.click()
                    time.sleep(20)
                    config["id_list"].append(ID)
                    break
                except NoSuchElementException:
                    logger.error(f"no retry flag")
                    wrong_time += 1
                    if wrong_time >= 2:
                        break
                time.sleep(1)
                continue

            logger.info(f"Count: {COUNT + 1}, {ID}, {Nickname}, {Description}, {dateCreated}, {homeLocation}, {follower}, {following}, {posts}")

            COUNT += 1
            data["ID"] = ID
            data["Nickname"] = Nickname
            data["Description"] = Description
            data["dateCreated"] = dateCreated
            data["homeLocation"] = homeLocation
            data["followers"] = follower
            data["following"] = following
            data["posts"] = posts
            result[ID] = data
            config["pbar"].update(1)
            break

    logger.info(f"user {config['id']}----{conf['token'][config['id']]} end, count_all = {COUNT}")
    driver_quit(driver)

    return result


def homepages(config):
    try:
        start_datetime = datetime.now()
        config["start_datetime"] = start_datetime
        if config["users"] == -1:
            config["users"] = len(conf['token'])

        id_lists = split_list_per_user(config["id_list"], config["users"])
        pbar = tqdm(total=len(config["id_list"]))
        config["pbar"] = pbar

        all_results = {}
        future2id = {}
        with ThreadPoolExecutor(max_workers=config["threads"]) as executor:
            for id in range(config["users"]):
                config["id_list"] = id_lists[id]
                config["id"] = id
                future = executor.submit(run_homepages, config)
                future2id[future] = id
            for future in concurrent.futures.as_completed(future2id):
                id = future2id[future]
                try:
                    sig_results = future.result()
                    all_results[conf['token'][id]] = sig_results
                except Exception as exc:
                    logger.error(f'User {id} generated an exception: {exc}')
    finally:
        save(all_results, "homepages", start_time=start_datetime)
        end_datetime = datetime.now()
        logger.info(f"File saved, total time: {end_datetime - start_datetime}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threads", type=int, default=1, help="Number of threads to use")
    parser.add_argument("--users", type=int, default=-1, help="Number of users to use")
    parser.add_argument("--id_list", nargs='+', default=["elonmusk", "NASA", "realDonaldTrump", "realDonaldTrump"], help="ID list to interact with")
    args = parser.parse_args()
    return args


def create_config(args):
    return dict(
        threads=args.threads,
        users=args.users,
        id_list=args.id_list
    )


def main():
    args = parse_args()
    config = create_config(args)
    homepages(config)


if __name__ == '__main__':
    main()

# python scrap_homepage.py --threads 1 --users 1 --url_list "elonmusk" "NASA" "realDonaldTrump" "realDonaldTrump"
