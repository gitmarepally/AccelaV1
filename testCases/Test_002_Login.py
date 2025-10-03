# testCases/Test_002_Login.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from pageObjects.LoginPage import LoginPage
from utilities.readProperties import ReadConfig


class Test_002_Login:

    baseURL = ReadConfig.getApplicationURL()
    username = ReadConfig.getUsername()
    password = ReadConfig.getPassword()

    @pytest.mark.sanity
    def test_login(self, setup):
        self.driver = setup
        self.driver.get(self.baseURL)
        self.driver.maximize_window()

        lp = LoginPage(self.driver, timeout=20)

        # set username/password with robust frame-handling
        lp.setUsername(self.username)
        lp.setPassword(self.password)
        lp.clickLogin()

        # Wait a bit for navigation / user-specific element.
        # Replace the locator below with a reliable post-login indicator for your app.
        # Example: presence of "Sign Out" link or user name label
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        wait = WebDriverWait(self.driver, 15)
        try:
            # Adjust this to a reliable post-login selector for your app
            user_menu = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(., 'Sign Out') or contains(., 'Sign out') or contains(., 'Logout') or contains(@class,'user')]")))
            assert True
        except Exception:
            # grab a screenshot for debugging
            self.driver.save_screenshot("login_failure.png")
            assert False, "Login failed - post-login element not found. See login_failure.png"
