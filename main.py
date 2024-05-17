"""
This module automates the voting process on the MMOTop website.
It includes classes for interacting with the web page and for managing the voting process.
"""

import logging
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from seleniumbase import SB
from seleniumbase.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementNotVisibleException,
)

from settings import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class MMOTopPage:
    """
    A class to interact with the MMOTop web page.
    """

    def __init__(self, driver):
        """
        Initialize the MMOTopPage instance.

        :param driver: The web driver for browser automation.
        """
        self.driver = driver

    def open_vote_page(self, url: str) -> None:
        """
        Open the voting page.

        :param url: The URL of the voting page.
        """
        logging.info("Opening vote page: %s", url)
        self.driver.uc_open_with_reconnect(url, reconnect_time=7)

    def login(self, user_name: str, user_password: str) -> None:
        """
        Log in to the MMOTop website.

        :param user_name: The username.
        :param user_password: The password.
        """
        logging.info("Logging in...")
        self.driver.uc_click(
            "//a[@href='https://mmotop.ru/users/sign_in']",
            by=By.XPATH,
            reconnect_time=5,
        )
        self.driver.send_keys("//input[@id='user_email']", user_name, by=By.XPATH)
        self.driver.send_keys(
            "//input[@id='user_password']", user_password, by=By.XPATH
        )
        self.driver.uc_click("//input[@name='sign_in']", by=By.XPATH, reconnect_time=5)

    def solve_qaptcha(self) -> None:
        """
        Solve the Qaptcha on the site.
        """
        slider = self.driver.wait_for_element_present(
            "//div[@class='Slider ui-draggable ui-draggable-handle']"
        )
        ActionChains(self.driver).drag_and_drop_by_offset(slider, 478, 0).perform()
        logging.info("Qaptcha solved!")
        self.driver.reconnect(3)

    def log_time_until_next_vote(self) -> None:
        """
        Log the remaining time until the next vote.
        """
        countdown_element = self.driver.wait_for_element_present(
            By.XPATH, "//span[@class='countdown_row countdown_amount']"
        )
        countdown_text = countdown_element.text
        logging.info("Time remaining until next vote: %s", countdown_text)

    def _solve_cloudflare_captcha(self):
        """
        Solve the Cloudflare captcha.
        """
        frame = self.driver.find_element(
            "//iframe[contains(@src, 'cloudflare.com')]", By.XPATH
        )
        self.driver.uc_switch_to_frame(frame)
        try:
            self.driver.find_element("//div[contains(@style, 'visible')]", By.XPATH)
        except NoSuchElementException:
            self.driver.uc_click(frame, reconnect_time=7)
            self.driver.find_element("//div[contains(@style, 'visible')]", By.XPATH)

    def vote(self, server_rate: str, account_name: str) -> None:
        """
        Perform the voting process.

        :param server_rate: The server rate to vote for.
        :param account_name: The account name used for voting.
        """
        logging.info("Voting for %s on server rate %s...", account_name, server_rate)
        self.driver.execute_script("window.scrollTo(0, 10000);")
        self.driver.uc_click(
            f"//td[contains(text(), '{server_rate}')]/../td/input[@type='radio']",
            by=By.XPATH,
            reconnect_time=3,
        )
        char_input = self.driver.find_element(By.XPATH, "//div[@id='charname']/input")
        char_input.clear()
        char_input.send_keys(account_name)
        self._solve_cloudflare_captcha()
        self.driver.reconnect(3)
        try:
            self.driver.click("//div/input[@type='submit']")
            logging.info("Vote successful!")
            time.sleep(10)
        except NoSuchElementException:
            logging.error("Captcha not solved!")


class MMOTopAutomation:
    """
    A class to manage the automation of the voting process on MMOTop.
    """

    def __init__(
        self,
        vote_url: str,
        user_name: str,
        user_password: str,
        server_rate: str,
        sirus_account_name: str,
        browser: str = "chrome",
    ):
        """
        Initialize the MMOTopAutomation instance.

        :param vote_url: The URL of the voting page.
        :param user_name: The username for login on mmotop.
        :param user_password: The password for login on mmotop.
        :param server_rate: The server rate to vote for.
        :param account_name: The sirus account name used for voting.
        :param browser: The browser to use for automation (default is "chrome").
        """
        self.vote_url = vote_url
        self.username = user_name
        self.password = user_password
        self.server_rate = server_rate
        self.sirus_account_name = sirus_account_name
        self.browser = browser

    def run(self) -> None:
        """
        Run the automated voting process.
        """
        with SB(
            browser=self.browser, uc=True, ad_block_on=True, page_load_strategy="none"
        ) as sb:
            driver = sb.driver
            page = MMOTopPage(driver)
            page.open_vote_page(self.vote_url)
            page.login(self.username, self.password)
            try:
                logging.info("Checking if already voted today...")
                page.log_time_until_next_vote()
            except NoSuchElementException:
                logging.info("Not voted today yet.")
                page.solve_qaptcha()
                page.vote(self.server_rate, self.sirus_account_name)


if __name__ == "__main__":
    try:
        automation = MMOTopAutomation(**config)
        automation.run()

    except NoSuchElementException as e:
        logging.error("Element not found: %s", e)

    except TimeoutException as e:
        logging.error("A timeout occurred: %s", e)

    except ElementNotVisibleException as e:
        logging.error("Element not visible: %s", e)
