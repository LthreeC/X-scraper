from datetime import datetime
import time
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Tweet:
    def __init__(self,
                 driver: webdriver.Chrome,
                 Ad: list):
        self.driver = driver
        self.Ad = Ad
        self.isEnd = False

        while True:
            try:
                self.tweet = self.__get_first_tweet()
                if self.isEnd:
                    break

                self.isMedia = self.__check_Media()
                self.original = self.__check_original()
                self.tweet_url = self.__get_tweet_url()
                self.tweet_date = self.__get_tweet_date()
                self.tweet_text = self.__get_tweet_text()
                self.tweet_author = self.__get_tweet_author()
                self.tweet_group = self.__get_tweet_group()
                self.tweet_lang = self.__get_tweet_lang()


            except TypeError:
                self.Ad.append(self.tweet)
                time.sleep(1)
                driver.execute_script("arguments[0].scrollIntoView(true);", self.tweet)
                time.sleep(1)
                continue

            except Exception:
                print(traceback.format_exc())
                time.sleep(1)
                input("An error occured: ")
                continue
            break

        self.__delete_tweet(self.tweet)

    def get_url(self) -> str:
        return self.tweet_url

    def get_date(self) -> str:
        return self.tweet_date

    def get_text(self) -> str:
        return self.tweet_text

    def get_group(self) -> str:
        return self.tweet_group

    def get_author(self) -> (str, str):
        return self.tweet_author

    def get_lang(self) -> str:
        return self.tweet_lang

    def __find_element_in_tweet_retry(self, by, value, retries=3):
        for i in range(retries):
            try:
                element = self.tweet.find_element(by, value)
                return element
            except StaleElementReferenceException:
                if i < retries - 1:
                    try:
                        print(f"Retrying to find element in tweet ({i + 1}/{retries})...")
                        self.tweet = self.__get_first_tweet()
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((by, value))
                        )
                    except Exception:
                        time.sleep(1)
                        continue
                else:
                    return None

    def __get_first_tweet(self) -> WebElement:
        MAX_ATTEMPTS = 10
        attempts = 0
        while attempts < MAX_ATTEMPTS:
            try:
                tweets = self.driver.find_elements(By.CSS_SELECTOR, "article[data-testid='tweet']")
                for tweet in tweets:
                    if tweet not in self.Ad:
                        return tweet
            except Exception:
                time.sleep(1)
                continue
            finally:
                attempts += 1
        self.isEnd = True
        return None

    def __remove_pinned(self):
        while True:
            try:
                if self.tweet.find_element(By.CSS_SELECTOR, 'div[data-testid="socialContext"]').get_attribute(
                        "innerText") == "Pinned":
                    print("Skipping pinned...")
                    raise TypeError
            except NoSuchElementException:
                pass
            except StaleElementReferenceException:
                time.sleep(1)
                continue
            break


    def __get_tweet_lang(self) -> str:
        try:
            element = self.__find_element_in_tweet_retry(By.CSS_SELECTOR, "div[data-testid='tweetText']")
            lang = element.get_attribute("lang")
            return lang
        except Exception:
            return "None"

    def __get_tweet_url(self) -> (str, bool):
        try:
            url = self.__find_element_in_tweet_retry(By.XPATH, ".//div[@data-testid='User-Name']/div[2]/div/div[3]//a[@role='link']").get_attribute("href")

        except NoSuchElementException:
            raise TypeError

        return url

    def __get_tweet_date(self) -> str:
        try:
            date = self.__find_element_in_tweet_retry(By.CSS_SELECTOR, "time").get_attribute("datetime")[:19]
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
        except NoSuchElementException:
            raise TypeError

        return date.strftime('%Y-%m-%d %H:%M:%S')

    #
    def __get_tweet_text(self) -> str:
        try:
            element = self.__find_element_in_tweet_retry(By.CSS_SELECTOR, "div[data-testid='tweetText']")

            return element.get_attribute("innerText")
        except NoSuchElementException:
            return ""

    def __get_tweet_author(self) -> str:
        try:
            element = self.__find_element_in_tweet_retry(By.XPATH, ".//div[@data-testid='User-Name']/div/div/a")
        except NoSuchElementException:
            return "", ""
        ID = element.get_attribute("href")
        segments = ID.split('/')
        ID = segments[-1]
        nickname = element.get_attribute("innerText")
        return ID, nickname

    def __check_Media(self) -> bool:
        try:
            Photo_flag = self.__find_element_in_tweet_retry(By.XPATH, ".//div[@data-testid='tweetPhoto']")
            if Photo_flag != None:
                return True
        except NoSuchElementException:
            try:
                Video_flag = self.__find_element_in_tweet_retry(By.XPATH, ".//div[@data-testid='videoPlayer']")
                if Video_flag != None:
                    return True
            except NoSuchElementException:
                return False

    def __check_original(self) -> bool:
        try:
            reposted_flag = self.__find_element_in_tweet_retry(By.XPATH,".//span[@data-testid='socialContext']")
            if reposted_flag != None:
                return False
        except NoSuchElementException:
            return True


    def __get_tweet_group(self):
        element = self.__find_element_in_tweet_retry(By.CSS_SELECTOR, "div[role='group']")
        if element is not None:
            return element.get_attribute("aria-label")
        return ""

    def __delete_tweet(self, param):
        self.driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """, param)
