import argparse
import concurrent
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import random

from tqdm import tqdm
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()

from module.Interaction import TweetRetweeter
from common.utils import load_conf, set_token, open_driver, driver_quit, split_list_per_user, save, get_full_page, random_mouse_movement
from common import get_logger

logger = get_logger("global")
conf = load_conf()
COUNT = 0


def run_interactions(config):
    global COUNT
    logger.info(config)
    result = {}

    driver = open_driver(conf["headless"], conf["userAgent"][config["id"] % len(conf["userAgent"])])
    logger.info(f"user {config['id']}----{conf['token'][config['id']]} starts")

    driver.get("https://twitter.com/")
    set_token(driver, conf["token"][config["id"]])

    for url in config["url_list"]:
        result[url] = {"quotes": [], "retweets": [], "likes": []}
        logger.info(f"current url: {url}")

        url_quotes = url + '/quotes'
        driver.get(url_quotes)
        get_full_page(driver, 2)
        time.sleep(random.uniform(0, 1))
        while True:
            COUNT += 1
            tr = TweetRetweeter(driver, "quotes")
            isEnd = tr.get_isEnd()
            if isEnd:
                logger.info("quotes END")
                break
            ID, Nickname = tr.get_tweet_retweeter()
            logger.info(f"COUNT: {COUNT}, ID: {ID}, Nickname: {Nickname}")
            result[url]["quotes"].append({"ID": ID, "Nickname": Nickname})

        url_retweets = url + '/retweets'
        driver.get(url_retweets)
        get_full_page(driver, 4)

        time.sleep(random.uniform(0, 1))
        while True:
            COUNT += 1
            tr = TweetRetweeter(driver, mode="retweets")
            isEnd = tr.get_isEnd()
            if isEnd:
                logger.info("retweets END")
                break
            ID, Nickname = tr.get_tweet_retweeter()
            logger.info(f"COUNT: {COUNT}, ID: {ID}, Nickname: {Nickname}")
            result[url]["retweets"].append({"ID": ID, "Nickname": Nickname})

        url_likes = url + '/likes'
        driver.get(url_likes)
        get_full_page(driver, 5)
        time.sleep(random.uniform(0, 1))
        while True:
            COUNT += 1
            tr = TweetRetweeter(driver, "likes")
            isEnd = tr.get_isEnd()
            if isEnd:
                logger.info("likes END")
                break
            ID, Nickname = tr.get_tweet_retweeter()
            logger.info(f"COUNT: {COUNT}, ID: {ID}, Nickname: {Nickname}")
            result[url]["likes"].append({"ID": ID, "Nickname": Nickname})
            if COUNT % 10 == 0: random_mouse_movement(driver)

        config["pbar"].update(1)

    logger.info(f"user {config['id']}----{conf['token'][config['id']]} end, count_all = {COUNT}")
    driver_quit(driver)

    return result


def interactions(config):
    try:
        start_datetime = datetime.now()
        config["start_datetime"] = start_datetime
        if config["users"] == -1:
            config["users"] = len(conf['token'])

        url_lists = split_list_per_user(config["url_list"], config["users"])
        pbar = tqdm(total=len(config["url_list"]))
        config["pbar"] = pbar

        all_results = {}
        future2id = {}
        with ThreadPoolExecutor(max_workers=config["threads"]) as executor:
            for id in range(config["users"]):
                config["url_list"] = url_lists[id]
                config["id"] = id
                future = executor.submit(run_interactions, config)
                future2id[future] = id
            for future in concurrent.futures.as_completed(future2id):
                id = future2id[future]
                try:
                    sig_results = future.result()
                    all_results[conf['token'][id]] = sig_results
                except Exception as exc:
                    logger.error(f'User {id} generated an exception: {exc}')
    finally:
        save(all_results, "interactions", start_time=start_datetime)
        end_datetime = datetime.now()
        logger.info(f"File saved, total time: {end_datetime - start_datetime}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threads", type=int, default=1, help="Number of threads to use")
    parser.add_argument("--users", type=int, default=-1, help="Number of users to use")
    parser.add_argument("--url_list", nargs='+', default=["https://x.com/MathVerseNFT/status/1899369827866685661", "https://x.com/MathVerseNFT/status/1874155560058196310"],
                        help="Url list to interact with")
    args = parser.parse_args()
    return args


def create_config(args):
    return dict(
        threads=args.threads,
        users=args.users,
        url_list=args.url_list
    )


def main():
    args = parse_args()
    config = create_config(args)
    interactions(config)


if __name__ == '__main__':
    main()

# python scrap_interactions.py --threads 1 --users 1 --url_list "https://x.com/MathVerseNFT/status/1899369827866685661" "https://x.com/MathVerseNFT/status/1874155560058196310"
