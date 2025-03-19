from time import sleep
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement


class TweetRetweeter:
    def __init__(self,
                 driver: webdriver.Chrome,
                 mode: str,
                 ):
        self.driver = driver
        self.isEnd = False

        while True:
            try:
                self.mode = mode
                self.tweet = self.__get_first_cell()
                if self.isEnd:
                    break
                if mode == "followings":
                    self.tweet_ID, self.tweet_nickname, self.tweet_content = self.__get_retweeter()
                else:
                    self.tweet_ID, self.tweet_nickname = self.__get_retweeter()
            except TypeError:
                sleep(2)
                continue
            except Exception:
                print(traceback.format_exc())
                sleep(2)
                continue
            break

        if not self.isEnd: self.__delete_tweet()

    def __delete_tweet(self):
        self.driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """, self.tweet)

    def get_isEnd(self) -> bool:
        return self.isEnd

    def get_tweet_retweeter(self) -> str:
        return self.tweet_ID, self.tweet_nickname

    def get_tweet_follow(self) -> str:
        return self.tweet_ID, self.tweet_nickname, self.tweet_content

    def __get_first_cell(self) -> WebElement:
        MAX_ATTEMPTS = 4
        attempts = 0
        while attempts < MAX_ATTEMPTS:
            try:
                tweet = WebDriverWait(self.driver, 2, 0.1).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@data-testid='cellInnerDiv']"))
                )
                if tweet.get_attribute('innerText') != "":
                    return tweet
                sleep(1)
            except Exception:
                sleep(1)
                continue
            finally:
                attempts += 1
        self.isEnd = True
        return "end."

    def __get_retweeter(self):
        if self.mode == "retweets" or self.mode == "likes":
            try:
                elements = self.tweet.find_elements(By.XPATH, ".//a[@role='link']")
                element = elements[0]
                for ele in elements:
                    if ele.get_attribute("innerText") != "":
                        element = ele
                        break
            except Exception:
                raise TypeError

            ID = element.get_attribute("href")
            segments = ID.split('/')
            ID = segments[-1]
            nickname = element.get_attribute("innerText")
            return ID, nickname

        elif self.mode == "quotes":
            try:
                element = self.tweet.find_element(By.XPATH, ".//div[@data-testid='User-Name']/div[1]/div/a")
            except Exception:
                raise TypeError

            ID = element.get_attribute("href")
            segments = ID.split('/')
            ID = segments[-1]
            nickname = element.get_attribute("innerText")
            return ID, nickname


        elif self.mode == "followings":
            try:
                elements = self.tweet.find_elements(By.XPATH, ".//a[@role='link']")
                try:
                    content = self.tweet.find_element(By.XPATH, ".//div[@dir='auto' and contains(@style, 'text-overflow')]").get_attribute("innerText")
                except NoSuchElementException:
                    content = ""
                element = elements[0]
                for ele in elements:
                    if ele.get_attribute("innerText") != "":
                        element = ele
                        break

            except Exception as e:
                print(e)
                raise TypeError

            ID = element.get_attribute("href")
            segments = ID.split('/')
            ID = segments[-1]
            nickname = element.get_attribute("innerText")
            return ID, nickname, content
