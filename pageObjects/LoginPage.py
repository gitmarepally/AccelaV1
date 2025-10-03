# pageObjects/LoginPage.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
)
import time

class LoginPage:
    # primary locators (use both id and name as fallback)
    _username_id = "username"
    _username_name = "username"
    _password_id = "password"
    _password_name = "password"
    _login_button_xpath = "//button[contains(normalize-space(.), 'Sign In') or contains(normalize-space(.), 'Sign in')]"

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def _find_visible(self, by, value, timeout=None):
        """Wait and return visible element or raise TimeoutException."""
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return wait.until(EC.visibility_of_element_located((by, value)))

    def _find_element_across_frames(self, by, value, timeout=5):
        """
        Try to find element in main document, otherwise iterate all iframes
        and return the first match. Leaves driver focused inside the frame
        where the element was found.
        """
        # 1) Try main document quickly
        try:
            return self._find_visible(by, value, timeout=timeout)
        except TimeoutException:
            pass

        # 2) Try each iframe
        frames = self.driver.find_elements(By.TAG_NAME, "iframe")
        for idx, frm in enumerate(frames):
            try:
                self.driver.switch_to.frame(frm)
                try:
                    el = self._find_visible(by, value, timeout=timeout)
                    return el
                except TimeoutException:
                    # not in this frame, continue to next
                    self.driver.switch_to.default_content()
                    continue
            except StaleElementReferenceException:
                # frame disappeared; continue
                self.driver.switch_to.default_content()
                continue
        # Not found anywhere: ensure we're back at default content
        self.driver.switch_to.default_content()
        raise NoSuchElementException(f"Element not found by {by}='{value}' in document or any iframe")

    def setUsername(self, username):
        # try by id then name
        try:
            el = self._find_element_across_frames(By.ID, self._username_id, timeout=3)
        except NoSuchElementException:
            el = self._find_element_across_frames(By.NAME, self._username_name, timeout=3)
        el.clear()
        el.send_keys(username)

    def setPassword(self, password):
        try:
            el = self._find_element_across_frames(By.ID, self._password_id, timeout=3)
        except NoSuchElementException:
            el = self._find_element_across_frames(By.NAME, self._password_name, timeout=3)
        el.clear()
        el.send_keys(password)

    def clickLogin(self):
        # login button might be outside the frame where inputs are, so:
        # try to find it in current context first, else search main + frames
        try:
            btn = self._find_visible(By.XPATH, self._login_button_xpath, timeout=3)
        except TimeoutException:
            # search across frames (this will switch to the frame containing the button)
            btn = self._find_element_across_frames(By.XPATH, self._login_button_xpath, timeout=3)

        btn.click()
        # After click, reset to default content to continue the test
        try:
            self.driver.switch_to.default_content()
        except Exception:
            pass