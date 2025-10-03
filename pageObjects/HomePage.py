
from selenium.webdriver.common.by import By


class HomePage:
    frame_xpath = "//iframe[@id='LoginFrame']"
    link_register_relative_xpath="//span[normalize-space()='Create an Account']"
    link_signup_relative_xpath="//span[@class='p-button-label']"

    def __init__(self, driver):
        self.driver = driver

    def clickRegister(self):
        iframe = self.driver.find_element(By.XPATH, self.frame_xpath)
        self.driver.switch_to.frame(iframe)
        self.driver.find_element(By.XPATH, self.link_register_relative_xpath).click()
        self.driver.switch_to.default_content()

    def clickSignup(self):
        iframe = self.driver.find_element(By.XPATH, self.frame_xpath)
        self.driver.switch_to.frame(iframe)
        self.driver.find_element(By.XPATH, self.link_signup_relative_xpath).click()
        self.driver.switch_to.default_content()
        #self.driver.find_element_by.xpath(self.link_login_relative_xpath).click()




#  for Data driven
# # pageObjects/HomePage.py
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
#
# class HomePage:
#     # keep whatever existing init you have, for example:
#     def __init__(self, driver):
#         self.driver = driver
#         # existing locators (adjust if yours differ)
#         self.frame_xpath = "//iframe[@id='LoginFrame']"
#         self.signup_button = (By.ID, "signupBtn")      # <-- example; replace with your actual locator
#         self.login_button_outside_iframe = (By.ID, "loginBtn")  # fallback button outside iframe
#
#     def clickSignup(self, timeout=8):
#         """
#         Try to switch into iframe if present and then perform actions.
#         If iframe not present within timeout, fallback to clicking a visible signup/login button outside the iframe.
#         """
#         wait = WebDriverWait(self.driver, timeout)
#         try:
#             # Wait for the iframe to be present and switch to it
#             iframe_el = wait.until(EC.presence_of_element_located((By.XPATH, self.frame_xpath)))
#             self.driver.switch_to.frame(iframe_el)
#             # If inside iframe you need to click the signup inside it; example:
#             try:
#                 signup_el = wait.until(EC.element_to_be_clickable(self.signup_button))
#                 signup_el.click()
#             except Exception:
#                 # if there is no signup inside iframe, just return and let caller interact
#                 return
#             finally:
#                 # switch back to default content so caller can proceed normally (or remove if you want to stay inside iframe)
#                 self.driver.switch_to.default_content()
#         except Exception:
#             # iframe didn't appear — attempt fallback click on outside login/signup button
#             try:
#                 btn = wait.until(EC.element_to_be_clickable(self.login_button_outside_iframe))
#                 btn.click()
#             except Exception:
#                 # nothing clickable found; raise so we get a good failure message
#                 raise






