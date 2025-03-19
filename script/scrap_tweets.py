import argparse
import time
from datetime import datetime
import concurrent
from concurrent.futures import ThreadPoolExecutor

import chromedriver_autoinstaller
# from commutil import dbg

chromedriver_autoinstaller.install()
from tqdm import tqdm
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from module.Tweet import Tweet
from common.utils import load_conf, set_token, driver_quit, open_driver, count_hours, save, split_list_per_user
from common import get_logger

logger = get_logger("global")
conf = load_conf()
COUNT = 0


def run_tweets(config):
    global COUNT
    logger.info(config)
    count_current = 0
    result = {}

    driver = open_driver(conf["headless"], conf["userAgent"][config["id"] % len(conf["userAgent"])])
    logger.info(f"user {config['id']}----{conf['token'][config['id']]} starts")

    for homepage in config["homepage_list"]:
        driver.get("https://twitter.com/")
        set_token(driver, conf["token"][config["id"]])
        driver.get("https://twitter.com/" + homepage)

        if homepage == 'home':
            Following_btn = WebDriverWait(driver, 16, 0.5).until(
                EC.presence_of_element_located((By.XPATH, "//span[text()='Following']"))
            )
            Following_btn.click()
            time.sleep(3)

        Ad = []
        wrong_time = 0
        wrong_T = 0

        while count_current < config["tweet_num"] and wrong_time < 100 and wrong_T < 100:
            try:
                tweet = Tweet(driver, Ad)
                if tweet.isEnd:
                    break
                wrong_time = 0
            except Exception as e:
                wrong_time += 1
                time.sleep(1)
                # logger.error(e)
                continue

            date = tweet.get_date()
            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            url = tweet.get_url()

            if (count_hours(start_datetime=config["start_datetime"], date=date, offset=0) > config["time_range"]):
                wrong_T += 1
                continue

            group = tweet.get_group()
            keywords = re.findall(r'reply|replies|repost|reposts|bookmark|bookmarks|like|likes|view|views', group)
            numbers = list(map(int, re.findall(r'\d+', group)))
            Replies = 0
            Reposts = 0
            Bookmarks = 0
            Likes = 0
            Views = 0
            for i, keyword in enumerate(keywords):
                if keyword == 'replies' or keyword == 'reply':
                    Replies = int(numbers[i])
                elif keyword == 'reposts' or keyword == 'repost':
                    Reposts = int(numbers[i])
                elif keyword == 'bookmarks' or keyword == 'bookmark':
                    Bookmarks = int(numbers[i])
                elif keyword == 'likes' or keyword == 'like':
                    Likes = int(numbers[i])
                elif keyword == 'views' or keyword == 'view':
                    Views = int(numbers[i])

            # logger.info(f"COUNT: {COUNT + 1}, User: {conf['token'][config['id']]} Date: {date}, URL: {url}, Group: {group}")
            logger.info(f"COUNT: {COUNT + 1},  User: {config['id']} Date: {date}, URL: {url}, Group: {group}")

            ID, nickname = tweet.get_author()
            text = tweet.get_text()
            lang = tweet.get_lang()

            count_current += 1
            COUNT += 1

            data = {"url": "", "ID": "", "Nickname": "", "Date": "", "isReposted": "", "isMedia": "", "Language": "", "Replies": "", "Reposts": "", "Likes": "", "Bookmarks": "", "Views": "", "Text": ""}
            data["url"] = url
            data["ID"] = ID
            data["Nickname"] = nickname
            data["isReposted"] = not tweet.original
            data["Date"] = date.strftime("%Y-%m-%d %H:%M:%S")
            data["Text"] = text
            data["Replies"] = Replies
            data["Reposts"] = Reposts
            data["Likes"] = Likes
            data["Bookmarks"] = Bookmarks
            data["Views"] = Views
            data["isMedia"] = tweet.isMedia
            data["Language"] = lang
            result[url] = data

        config["pbar"].update(1)

    logger.info(f"user {config['id']}----{conf['token'][config['id']]} end，count_current = {count_current}, count_all = {COUNT}")
    driver_quit(driver)
    return result


def tweets(config):
    try:
        start_datetime = datetime.now()
        config["start_datetime"] = start_datetime
        if config["users"] == -1:
            config["users"] = len(conf['token'])

        homepage_lists = split_list_per_user(config["homepage_list"], config["users"])

        pbar = tqdm(total=len(config["homepage_list"]))
        config["pbar"] = pbar

        all_results = {}
        future2id = {}
        with ThreadPoolExecutor(max_workers=config["threads"]) as executor:
            for id in range(config["users"]):
                config["homepage_list"] = homepage_lists[id]
                config["id"] = id
                future = executor.submit(run_tweets, config)
                future2id[future] = id
            for future in concurrent.futures.as_completed(future2id):
                id = future2id[future]
                try:
                    sig_results = future.result()
                    all_results[conf['token'][id]] = sig_results
                except Exception as exc:
                    logger.error(f'User {id} generated an exception: {exc}')
    finally:
        save(all_results, "tweets", start_time=start_datetime)
        end_datetime = datetime.now()
        logger.info(f"File saved, total time: {end_datetime - start_datetime}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threads", type=int, default=1, help="Number of threads to use")
    parser.add_argument("--users", type=int, default=-1, help="Number of users to use")
    parser.add_argument("--tweet_num", type=int, default=100, help="Number of tweets per user")
    parser.add_argument("--time_range", type=int, default=240, help="Time range to scrape in hours")

    parser.add_argument("--homepage_list", nargs='+', default=['home'], help="Homepage list")

    args = parser.parse_args()
    return args


def create_config(args):
    return dict(
        threads=args.threads,
        users=args.users,
        tweet_num=args.tweet_num,
        time_range=args.time_range,
        homepage_list=args.homepage_list
    )


def main():
    args = parse_args()
    config = create_config(args)
    tweets(config)


if __name__ == '__main__':
    main()

# python scrap_tweets.py --threads 1 --users -1 --tweet_num 100 --time_range 240 --homepage_list home