# pageObjects/AccountRegistrationPage.py
import logging
import time

from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    ElementClickInterceptedException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

logger = logging.getLogger(__name__)


class AccountRegistrationPage:
    # --- locators ---
    txt_username_name = "txbUserName"
    txt_password_name = "txbPassword1"
    txt_type_password_again_name = "txbPassword2"

    # generic dropdown trigger (may need to be made more specific if page has >1 dropdowns)
    ddb_enter_security_question_xpath = "//div[contains(@class,'p-dropdown-trigger')]"
    dropdown_items_xpath = "//li[contains(@class,'p-dropdown-item')]"  # PrimeNG items
    role_option_xpath = "//li[@role='option']"  # fallback options

    txt_security_answer_name = "txbAnswer"
    chk_receive_sms_message_xpath = "//p-checkbox[@id='cbReceiveSMS']//div[contains(@class,'p-checkbox-box')]"
    # terms of service may be cbDisclaimer; keep fallback logic
    chk_terms_of_service_xpath_primary = "//p-checkbox[@id='cbDisclaimer']//div[contains(@class,'p-checkbox-box')]"
    chk_terms_of_service_xpath_fallback = "//p-checkbox[@id='cbReceiveSMS']//div[contains(@class,'p-checkbox-box')]"

    txt_email_address_name = "txbEmail"
    txt_mobile_phone_xpath = "//input[@id='txbMobilePhone']"

    btn_continue_xpath = "//span[normalize-space()='Continue']"
    ddb_contact_details_for = "//div[contains(@class,'p-dropdown-trigger')]"  # make more specific if needed
    txt_contact_first_name = "txtAppFirstName"
    txt_contact_last_name = "txtAppLastName"
    btn_submit_xpath = "//span[normalize-space()='Submit']"

    txt_confirmation_msg_xpath = (
        "/html[1]/body[1]/form[1]/div[3]/div[1]/div[7]/div[1]/div[1]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[3]"
    )

    def __init__(self, driver, timeout=12):
        """
        :param driver: selenium webdriver
        :param timeout: default explicit wait timeout (seconds)
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # --- low-level helpers ---

    def _safe_click(self, by_locator, retries=3, poll=0.2):
        """
        Robust click:
         - wait until clickable
         - scroll into view
         - move to element
         - try normal click
         - on ElementClickInterceptedException try ESC + body click then JS click
         - retry on StaleElementReferenceException
        :param by_locator: tuple (By, locator)
        """
        attempt = 0
        last_exc = None
        while attempt < retries:
            attempt += 1
            try:
                el = self.wait.until(EC.element_to_be_clickable(by_locator))

                # scroll to center
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                except Exception:
                    pass

                # hover to ensure not obstructed
                try:
                    ActionChains(self.driver).move_to_element(el).pause(0.05).perform()
                except Exception:
                    pass

                try:
                    el.click()
                    return
                except ElementClickInterceptedException as e:
                    logger.warning("Click intercepted on attempt %s for %s: %s", attempt, by_locator, e)

                    # try to dismiss overlays/tooltips
                    try:
                        ActionChains(self.driver).send_keys("\u001b").perform()  # ESC
                    except Exception:
                        pass
                    try:
                        self.driver.execute_script("document.body.click();")
                    except Exception:
                        pass

                    time.sleep(0.25)

                    # fallback to JS click
                    try:
                        self.driver.execute_script("arguments[0].click();", el)
                        return
                    except Exception as e_js:
                        last_exc = e_js
                        logger.debug("JS click failed: %s", e_js)
                        time.sleep(poll)
                        continue

                except StaleElementReferenceException as e:
                    last_exc = e
                    logger.debug("Stale element, retrying... (%s/%s)", attempt, retries)
                    time.sleep(poll)
                    continue

            except TimeoutException as e:
                logger.exception("Timeout waiting for element to be clickable: %s", by_locator)
                raise
            except StaleElementReferenceException as e:
                last_exc = e
                logger.debug("Stale while locating element, retrying... (%s/%s)", attempt, retries)
                time.sleep(poll)
                continue

        # exhausted retries
        if last_exc:
            raise last_exc
        raise ElementClickInterceptedException(f"Could not click element after {retries} attempts: {by_locator}")

    def _safe_send_keys(self, by_locator, text, clear_first=True):
        """
        Wait for presence and send keys (with optional clear).
        """
        try:
            el = self.wait.until(EC.presence_of_element_located(by_locator))
            if clear_first:
                try:
                    el.clear()
                except Exception:
                    pass
            el.send_keys(text)
        except TimeoutException:
            logger.exception("Timeout waiting for element to send keys: %s", by_locator)
            raise

    # --- page actions ---

    def setUserName(self, uname):
        self._safe_send_keys((By.NAME, self.txt_username_name), uname)

    def setPassword(self, pwd):
        self._safe_send_keys((By.NAME, self.txt_password_name), pwd)

    def setType_Password_Again(self, pwd_again):
        self._safe_send_keys((By.NAME, self.txt_type_password_again_name), pwd_again)

    def setEnter_Security_Question(self):
        """
        Open the security question dropdown. Defensive attempt to dismiss overlays first.
        """
        try:
            ActionChains(self.driver).send_keys("\u001b").perform()  # ESC to dismiss
            self.driver.execute_script("document.body.click();")
        except Exception:
            pass

        self._safe_click((By.XPATH, self.ddb_enter_security_question_xpath))

    def setEnter_Security_Question2(self, text):
        """
        Open dropdown and select option by visible text.
        """
        self.setEnter_Security_Question()

        # exact-match first
        option_xpath_exact = f"{self.dropdown_items_xpath}[normalize-space(.)='{text}']"
        option_xpath_contains = f"{self.dropdown_items_xpath}[contains(normalize-space(.), '{text}')]"
        role_exact = f"{self.role_option_xpath}[normalize-space(.)='{text}']"
        role_contains = f"{self.role_option_xpath}[contains(normalize-space(.), '{text}')]"

        tried = []
        for xpath in (role_exact, option_xpath_exact, role_contains, option_xpath_contains):
            tried.append(xpath)
            try:
                self._safe_click((By.XPATH, xpath))
                return
            except TimeoutException:
                # try next
                logger.debug("Option not found/clickable for xpath: %s", xpath)
                continue
            except Exception as e:
                logger.debug("Unexpected while selecting security question option (%s): %s", xpath, e)
                continue

        raise TimeoutException(f"Could not find/select security question option '{text}'. Tried: {tried}")

    def setSecurity_Answer(self, security_answer):
        self._safe_send_keys((By.NAME, self.txt_security_answer_name), security_answer)

    def setReceive_Sms_Message(self):
        self._safe_click((By.XPATH, self.chk_receive_sms_message_xpath))

    def setEmail_Address(self, email):
        self._safe_send_keys((By.NAME, self.txt_email_address_name), email)

    def setMobile_Phone(self, phone):
        phone = str(phone)
        self._safe_send_keys((By.XPATH, self.txt_mobile_phone_xpath), phone)

    def setTerms_of_Service(self):
        """
        Try primary locator first (cbDisclaimer), otherwise fallback.
        """
        try:
            self._safe_click((By.XPATH, self.chk_terms_of_service_xpath_primary))
        except Exception:
            logger.debug("Terms checkbox primary locator failed; trying fallback.")
            self._safe_click((By.XPATH, self.chk_terms_of_service_xpath_fallback))

    def clickContinue(self):
        self._safe_click((By.XPATH, self.btn_continue_xpath))

    def open_contact_dropdown(self):
        """
        Open contact dropdown and wait briefly for options to appear.
        """
        self._safe_click((By.XPATH, self.ddb_contact_details_for))

        # wait for either role-based or generic items to appear (non-fatal)
        try:
            self.wait.until(EC.visibility_of_any_elements_located((By.XPATH, self.role_option_xpath)))
        except Exception:
            try:
                self.wait.until(EC.visibility_of_any_elements_located((By.XPATH, self.dropdown_items_xpath)))
            except Exception:
                logger.debug("Contact dropdown opened but no visible options detected immediately.")

    def select_contact_type_by_text(self, text, timeout: int = None):
        """
        Select contact type by matching visible option text.
        Will try role-based options first, then PrimeNG items. Falls back to JS clicking if needed.
        """
        self.open_contact_dropdown()
        local_wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)

        # gather candidates: role-based first, then generic
        candidates = []
        tried_selectors = []
        try:
            tried_selectors.append(self.role_option_xpath)
            candidates = local_wait.until(EC.visibility_of_all_elements_located((By.XPATH, self.role_option_xpath)))
        except Exception:
            try:
                tried_selectors.append(self.dropdown_items_xpath)
                candidates = local_wait.until(EC.visibility_of_all_elements_located((By.XPATH, self.dropdown_items_xpath)))
            except Exception:
                raise TimeoutException(f"No contact dropdown options found. Tried: {tried_selectors}")

        target = text.strip()
        target_lower = target.lower()

        visible_texts = []
        for el in candidates:
            try:
                item_text = el.text.strip()
            except Exception:
                continue
            if not item_text:
                continue
            visible_texts.append(item_text)
            if item_text == target or item_text.lower() == target_lower:
                # try normal click then JS fallback
                try:
                    try:
                        ActionChains(self.driver).move_to_element(el).pause(0.05).perform()
                    except Exception:
                        pass
                    el.click()
                    return
                except Exception as e_click:
                    logger.warning("Normal click failed for contact option '%s': %s; trying JS click", item_text, e_click)
                    try:
                        self.driver.execute_script("arguments[0].click();", el)
                        return
                    except Exception as e_js:
                        logger.exception("JS click failed for contact option '%s': %s", item_text, e_js)
                        # continue to try other candidates

        raise TimeoutException(
            f"Could not find/select contact option matching '{text}'. Visible options: {visible_texts}"
        )

    def setContactFirstName(self, cfirstname):
        self._safe_send_keys((By.NAME, self.txt_contact_first_name), cfirstname)

    def setContactLastName(self, clastname):
        self._safe_send_keys((By.NAME, self.txt_contact_last_name), clastname)

    def clickSubmit(self):
        self._safe_click((By.XPATH, self.btn_submit_xpath))

    def getconfirmationmsg(self, timeout_seconds: int = 6):
        """
        Return confirmation message text or None.
        """
        try:
            wait_local = WebDriverWait(self.driver, timeout_seconds)
            el = wait_local.until(EC.visibility_of_element_located((By.XPATH, self.txt_confirmation_msg_xpath)))
            return el.text.strip()
        except TimeoutException:
            logger.info("Confirmation message not found within seconds.", timeout_seconds)
            return None
        except Exception:
            logger.exception("Unexpected error retrieving confirmation message.")
            return None
