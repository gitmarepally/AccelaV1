import os
import time
import pytest
from pageObjects.AccountRegistrationPage import AccountRegistrationPage
from pageObjects.HomePage import HomePage
from utilities import randomeString
from utilities.readProperties import ReadConfig
from utilities.customLogger import LogGen

class Test_001_AccountRegistration:
    baseurl = ReadConfig.getApplicationURL() # variable baseurl to launch app -- not to hardcode the data
    logger=LogGen.loggen()

    @pytest.mark.regression
    def test_001_AccountRegistration(self, setup):

        """
        Test flow:
         - open homepage
         - click register
         - fill registration form
         - submit and assert confirmation message
        """
        # setup provides a WebDriver instance
        #self.logger.info("test log")
        #self.logger.warn('Test_001_AccountRegistration')
        #self.logger.info("Account Registration is started")
        self.logger.info("*** test_001_AccountRegistration ***")
        driver = setup
        try:
            #driver.get(ReadConfig.getApplicationURL())
            driver.get(self.baseurl)
            self.logger.info("launching page")
            driver.maximize_window()

            # small explicit wait for page load (replace with better waits in real code)
            time.sleep(1)

            hp = HomePage(driver)

            # Use page object method to open registration. If this element is inside an iframe
            # make sure clickRegister() handles switching to that iframe — otherwise update HP page object.
            hp.clickRegister()
            self.logger.info("Clicked Registration page")

            # instantiate registration page object
            regpage = AccountRegistrationPage(driver)

            # Generate username and email
            username = randomeString.random_string_generator()
            email = randomeString.random_string_generator() + "@gmail.com"

            # Fill the form (keeps your page object method names)
            regpage.setUserName(username)
            regpage.setPassword("Test1234@")
            regpage.setType_Password_Again("Test1234@")

            # If your setEnter_Security_Question2 expects the question string, keep it; otherwise update as needed
            regpage.setEnter_Security_Question2(
                "In what city or town does your nearest sibling live?"
            )
            regpage.setSecurity_Answer("USA")

            # If this is a checkbox/radio method, ensure it toggles correctly
            regpage.setReceive_Sms_Message()

            # Mobile number: pass as string to avoid integer truncation/locale issues
            regpage.setMobile_Phone("1249674359")
            self.logger.error("Missing phone number")

            regpage.setEmail_Address(email)

            regpage.setTerms_of_Service()
            regpage.clickContinue()

            # Contact details
            regpage.select_contact_type_by_text("Test")
            regpage.setContactFirstName(randomeString.random_string_generator())
            regpage.setContactLastName(randomeString.random_string_generator())

            regpage.clickSubmit()

            # Give a little time for confirmation to appear; replace with explicit wait in page object
            time.sleep(2)

            confmsg = regpage.getconfirmationmsg()

            # Close browser (quit/close in finally would be safer; using driver.quit() if available)
            driver.close()

            # Assert the expected confirmation message
            assert confmsg == "Your account is successfully registered.", (
                f"Unexpected confirmation message: {confmsg}")

            if confmsg != "Your account is successfully registered.":
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                driver.save_screenshot(f"screenshots/registration_fail_{timestamp}.png")


        except Exception:
            # ensure browser is closed on unexpected errors
            try:
                driver.quit()
            except Exception:
                pass
            raise
        self.logger.info("Account registration complete")

