from selenium.webdriver.common.by import By

class Dashboard():

    link_logout_relative_xpath="//span[@id='ctl00_HeaderNavigation_com_headIsLoggedInStatus_label_logout']"
    instruction_relative_xpath="//font[normalize-space()='TESTED']"

    def __init__(self, driver):
        self.driver = driver

    def isDashboardExist(self):
        try:
            elems=self.driver.find_element(By.XPATH, self.link_logout_relative_xpath).click()
            return len(elems) > 0
        except Exception:
            return False

    # def clickLogout(self):
    #     self.driver.find_element_by_xpath(self.link_logout_relative_xpath).click()


