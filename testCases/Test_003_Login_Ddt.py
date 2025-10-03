

# testCases/Test_003_Login_Ddt.py
import os
import time
import datetime
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pageObjects.Dashboard import Dashboard
from pageObjects.HomePage import HomePage
from pageObjects.LoginPage import LoginPage
from utilities import XLUtils
from utilities.readProperties import ReadConfig
from utilities.customLogger import LogGen


class Test_Login_DDT:
    baseURL = ReadConfig.getApplicationURL()
    logger = LogGen.loggen()

    base_path = os.path.abspath(os.curdir)
    testdata_dir = os.path.join(base_path, "testData")
    os.makedirs(testdata_dir, exist_ok=True)
    log_file = os.path.join(testdata_dir, "Accela_LoginData.xlsx")

    # directory to dump failure artifacts
    fail_artifacts_dir = os.path.join(testdata_dir, "fail_artifacts")
    os.makedirs(fail_artifacts_dir, exist_ok=True)

    def take_failure_artifacts(self, driver, row):
        """Save screenshot and page source for debugging."""
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(self.fail_artifacts_dir, f"row{row}_{ts}.png")
        html_path = os.path.join(self.fail_artifacts_dir, f"row{row}_{ts}.html")
        try:
            driver.save_screenshot(screenshot_path)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            self.logger.error(f"Saved failure artifacts for row {row}: {screenshot_path}, {html_path}")
        except Exception as e:
            self.logger.error(f"Could not save artifacts for row {row}: {e}")

    def test_login_ddt(self, setup):
        self.logger.info("*** Starting Test Login DDT ***")

        # read test data rows
        try:
            rows = XLUtils.getRowCount(self.log_file, "Sheet1")
            if rows < 2:
                pytest.fail("Test data sheet 'Sheet1' appears empty or only has header.")
        except Exception as e:
            self.logger.error(f"Failed to read test data file: {e}")
            pytest.fail("Test data file unreadable")

        driver = setup
        wait = WebDriverWait(driver, 12)

        lst_status = []
        row_results = []  # keep tuple (row, status, reason)

        try:
            driver.get(self.baseURL)
            driver.maximize_window()

            hp = HomePage(driver)
            lpg = LoginPage(driver)
            dp = Dashboard(driver)

            # loop rows
            for r in range(2, rows + 1):
                # make sure we're in default content before doing anything (important if previous row switched to iframe)
                try:
                    driver.switch_to.default_content()
                except Exception:
                    pass

                try:
                    self.logger.info(f"Processing row {r} ...")
                    # robustly open login/signup area (should handle iframe internally)
                    hp.clickSignup()

                    # read test data
                    username = XLUtils.readData(self.log_file, "Sheet1", r, 1)
                    password = XLUtils.readData(self.log_file, "Sheet1", r, 2)
                    expected = (XLUtils.readData(self.log_file, "Sheet1", r, 3) or "").strip().lower()

                    # set credentials (use waits if your page needs it)
                    lpg.setUsername(username)
                    lpg.setPassword(password)
                    # click login and wait for either dashboard or error message (adjust locators as needed)
                    lpg.clickLogin()

                    # give the app a moment to react, but prefer waiting for a dashboard indicator or a login error
                    actual_on_dashboard = False
                    try:
                        # prefer page-object method if available
                        actual_on_dashboard = bool(lpg.isDashboardExists())
                    except Exception:
                        # fallback: wait for dashboard heading or logout element
                        try:
                            # adjust locator to a reliable dashboard element in your app
                            wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Dashboard') or contains(., 'Welcome')]")))
                            actual_on_dashboard = True
                        except Exception:
                            actual_on_dashboard = False

                    # Optionally detect a visible login error message (tune xpath to your app)
                    login_error_visible = False
                    try:
                        # common error patterns: element with class 'error' or specific message area
                        err = driver.find_elements(By.XPATH, "//*[contains(@class,'error') or contains(@class,'alert')][contains(.,'invalid') or contains(.,'Incorrect') or contains(.,'failed')]")
                        if err:
                            login_error_visible = True
                    except Exception:
                        login_error_visible = False

                    # Evaluate expected vs actual
                    reason = ""
                    if actual_on_dashboard:
                        if expected == "valid":
                            status = "Pass"
                            reason = "Logged in and expected Valid"
                            # logout for next iteration
                            try:
                                dp.clickLogout()
                                # ensure logout completes
                                time.sleep(1)
                                driver.switch_to.default_content()
                            except Exception:
                                # if logout fails, continue (we'll catch on next iteration)
                                self.logger.warning("Logout attempt failed or not implemented")
                        else:
                            status = "Fail"
                            reason = "Logged in but expected Invalid"
                            # capture artifacts for investigation
                            self.take_failure_artifacts(driver, r)
                            try:
                                dp.clickLogout()
                                time.sleep(1)
                                driver.switch_to.default_content()
                            except Exception:
                                pass
                    else:
                        # not on dashboard
                        if expected == "valid":
                            status = "Fail"
                            if login_error_visible:
                                reason = "Not logged in (login error shown) but expected Valid"
                            else:
                                reason = "Not logged in (no dashboard) but expected Valid"
                            self.take_failure_artifacts(driver, r)
                        else:
                            status = "Pass"
                            reason = "Login failed as expected (Invalid)"

                    lst_status.append(status)
                    row_results.append((r, status, reason))
                    self.logger.info(f"Row {r} => {status}: {reason}")

                except Exception as row_exc:
                    # row-level failure: log, save artifacts, and mark Fail
                    self.logger.exception(f"Exception while processing row {r}: {row_exc}")
                    lst_status.append("Fail")
                    row_results.append((r, "Fail", f"Exception: {row_exc}"))
                    try:
                        self.take_failure_artifacts(driver, r)
                    except Exception:
                        pass
                    # attempt to restore context for next row
                    try:
                        driver.switch_to.default_content()
                    except Exception:
                        pass
                    # continue with next row

            # end for rows

            # summarize results in logger
            self.logger.info("DDT results per row:")
            for rr in row_results:
                self.logger.info(f"Row {rr[0]} => {rr[1]} : {rr[2]}")

            # final assertion
            failed_rows = [r for (r, s, _) in row_results if s == "Fail"]
            if not failed_rows:
                self.logger.info("*** Login DDT: All test cases passed ***")
                assert True
            else:
                self.logger.error(f"*** Login DDT: Failed rows: {failed_rows} ***")
                # fail with helpful message so pytest shows which rows failed
                pytest.fail(f"Login DDT failed for rows: {failed_rows}. See {self.fail_artifacts_dir} for screenshots/page sources.")

        finally:
            # ensure driver cleanup
            try:
                driver.quit()
            except Exception:
                pass





#
# # testCases/Test_003_Login_Ddt.py
# import time
# import pytest
# import os
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
#
# from pageObjects.Dashboard import Dashboard
# from pageObjects.HomePage import HomePage
# from pageObjects.LoginPage import LoginPage
# from utilities import XLUtils
# from utilities.readProperties import ReadConfig
# from utilities.customLogger import LogGen
#
#
# class Test_Login_DDT:
#     baseURL = ReadConfig.getApplicationURL()
#     logger = LogGen.loggen()
#
#     path = os.path.abspath(os.curdir)
#     testdata_dir = os.path.join(path, "testData")
#     os.makedirs(testdata_dir, exist_ok=True)
#     log_file = os.path.join(testdata_dir, "Accela_LoginData.xlsx")  # make sure file exists
#
#     def test_login_ddt(self, setup):
#         self.logger.info("*** Starting Test Login DDT ***")
#
#         try:
#             rows = XLUtils.getRowCount(self.log_file, "Sheet1")
#         except Exception as e:
#             self.logger.error(f"Failed to read test data file: {e}")
#             pytest.fail("Test data file unreadable")
#
#         lst_status = []
#         driver = setup
#         try:
#             driver.get(self.baseURL)
#             driver.maximize_window()
#             wait = WebDriverWait(driver, 10)
#
#             hp = HomePage(driver)
#             lpg = LoginPage(driver)
#             dp = Dashboard(driver)
#
#             for r in range(2, rows + 1):
#                 try:
#                     # robust navigation to login / signup area
#                     hp.clickSignup()
#
#                     username = XLUtils.readData(self.log_file, "Sheet1", r, 1)
#                     password = XLUtils.readData(self.log_file, "Sheet1", r, 2)
#                     expected = XLUtils.readData(self.log_file, "Sheet1", r, 3)
#
#                     lpg.setUsername(username)
#                     lpg.setPassword(password)
#                     lpg.clickLogin()
#
#                     # wait a bit for page change / dashboard presence
#                     time.sleep(2)
#
#                     # Use a reliable indicator for successful login.
#                     # Prefer implementing isDashboardExists() in LoginPage or Dashboard.
#                     actual_on_dashboard = False
#                     try:
#                         actual_on_dashboard = lpg.isDashboardExists()
#                     except Exception:
#                         # fallback: check for a known element on dashboard (adjust locator)
#                         try:
#                             dashboard_indicator = wait.until(
#                                 EC.presence_of_element_located((By.XPATH, "//h1[text()='Dashboard']"))
#                             )
#                             actual_on_dashboard = bool(dashboard_indicator)
#                         except Exception:
#                             actual_on_dashboard = False
#
#                     # Evaluate expected vs actual
#                     if actual_on_dashboard:
#                         if expected.strip().lower() == "valid":
#                             lst_status.append("Pass")
#                             # attempt logout for next iteration (adjust method name if necessary)
#                             try:
#                                 dp.clickLogout()
#                                 # give time to logout
#                                 time.sleep(1)
#                             except Exception:
#                                 # continue anyway
#                                 pass
#                         else:
#                             lst_status.append("Fail")
#                             try:
#                                 dp.clickLogout()
#                                 time.sleep(1)
#                             except Exception:
#                                 pass
#                     else:
#                         if expected.strip().lower() == "valid":
#                             lst_status.append("Fail")
#                         else:
#                             lst_status.append("Pass")
#
#                 except Exception as row_exc:
#                     # log row-level failure but continue with other rows
#                     self.logger.error(f"Row {r} raised exception: {row_exc}")
#                     lst_status.append("Fail")
#                     # try to restore to default content (in case we were inside an iframe)
#                     try:
#                         driver.switch_to.default_content()
#                     except Exception:
#                         pass
#
#             # final assertion after all rows processed
#             if "Fail" not in lst_status:
#                 self.logger.info("*** Login DDT: All test cases passed ***")
#                 assert True
#             else:
#                 self.logger.error(f"*** Login DDT: Some test cases failed: {lst_status} ***")
#                 assert False
#
#         finally:
#             # ensure driver quits even if assertion or other error occurs
#             try:
#                 driver.quit()
#             except Exception:
#                 pass




# import time
#
# import pytest
#
# from pageObjects.Dashboard import Dashboard
# from pageObjects.HomePage import HomePage
# from pageObjects.LoginPage import LoginPage
# from utilities import XLUtils
# from utilities.readProperties import ReadConfig
# from utilities.customLogger import LogGen
# import os
#
# class Test_Login_DDT():
#     baseURL = ReadConfig.getApplicationURL()
#     logger=LogGen.loggen()
#
#     path = os.path.abspath(os.curdir)
#     log_dir = os.path.join(path, 'testData')
#     os.makedirs(log_dir, exist_ok=True)
#     log_file = os.path.join(log_dir, "Accela_LoginData.Xlsx")
#
#
# def test_login_ddt(self, setup):
#     self.logger.info('*** Starting Test Login DDT ***')
#     self.rows=XLUtils.getRowCount(self.path, 'sheet1')
#     lst_status=[]
#     self.driver=setup
#     self.driver.get(self.baseURL)
#     self.driver.maximize_window()
#
#     self.hp=HomePage(self.driver)
#     self.lpg=LoginPage(self.driver)
#     self.dp=Dashboard(self.driver)
#
#     for r in range(2, self.rows+1):
#         self.hp.clickSignup()
#
#
#         self.username=XLUtils.readData(self.path, 'Sheet1', r, 1)
#         self.password=XLUtils.readData(self.path, 'Sheet1', r, 2)
#         self.exp=XLUtils.readData(self.path, 'Sheet1', r, 3)
#         self.lpg.setUsername(self.username)
#         self.lpg.setPassword(self.password)
#         self.lpg.clickLogin()
#         time.sleep(3)
#         #self.targetpage=self.lpg.isDashboardExists()
#
#         if self.exp=='Valid':
#             lst_status.append('Pass')
#             self.ma.clickLogout()
#             else:
#             lst_status.append('Fail')
#         elif self.exp=='Invalid':
#             lst_status.append('Fail')
#             else:
#             lst_status.append('Pass')
#         self.driver.close()
#         if 'Fail' not in lst_status:
#             assert True
#         else:
#             assert False
#         self.logger.info('*** Login Successful ***')