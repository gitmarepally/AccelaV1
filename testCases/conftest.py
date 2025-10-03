# conftest.py
import datetime
import os.path
import os

import pytest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import  EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from datetime import datetime



@pytest.fixture()
def setup(browser):
    if browser == "Edge":
        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
        print("Launching Edge browser...")
    elif browser == "Firefox":
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        print("Launching Firefox browser...")
    else:
        driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        print("Launching Chrome browser...")
    driver.maximize_window()

    # provide driver to test
    yield driver

    # teardown code after test completes
    print("Closing browser...")
    driver.quit()

def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="store",
        default="Chrome",
        help="Type of browser: Chrome, Firefox, Edge")


@pytest.fixture()
def browser(request):
    return request.config.getoption("browser")




#### PyTest HTML Report ####

# Hook for configuring metadata and report path
@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    # ✅ Add Environment info to HTML Report
    config.metadata = getattr(config, "metadata", {})
    config.metadata['Project Name'] = 'Accela'
    config.metadata['Module Name'] = 'CustRegistration'
    config.metadata['Tester Name'] = 'Sharath Chandra M'

    # ✅ Set report folder location with timestamp
    report_dir = os.path.join(os.path.abspath(os.curdir), "reports")
    os.makedirs(report_dir, exist_ok=True)   # ensure folder exists

    report_file = datetime.now().strftime("%Y%m%d-%H%M%S") + ".html"
    config.option.htmlpath = os.path.join(report_dir, report_file)

# Hook to delete/modify default Environment info
@pytest.mark.optionalhook
def pytest_metadata(metadata):
    metadata.pop("JAVA_HOME", None)
    metadata.pop("Plugins", None)










# import pytest
# import logging
# from selenium import webdriver
# from selenium.webdriver.firefox.service import Service as FirefoxService
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.firefox import GeckoDriverManager
# from webdriver_manager.chrome import ChromeDriverManager
#
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# if not logger.hasHandlers():
#     ch = logging.StreamHandler()
#     ch.setLevel(logging.INFO)
#     fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#     ch.setFormatter(fmt)
#     logger.addHandler(ch)
#
# def pytest_addoption(parser):
#     parser.addoption(
#         "--browser", action="store", default="chrome",
#         help="Browser to run tests against: chrome or firefox"
#     )
#     parser.addoption(
#         "--headless", action="store_true", default=False,
#         help="Run browser in headless mode"
#     )
#
# @pytest.fixture(scope="function")
# def setup(request):
#     browser = request.config.getoption("--browser").lower()
#     headless = request.config.getoption("--headless")
#     driver = None
#
#     try:
#         if browser == "firefox":
#             from selenium.webdriver.firefox.options import Options as FirefoxOptions
#             options = FirefoxOptions()
#             if headless:
#                 options.headless = True
#             service = FirefoxService(GeckoDriverManager().install())
#             driver = webdriver.Firefox(service=service, options=options)
#
#         elif browser == "chrome":
#             from selenium.webdriver.chrome.options import Options as ChromeOptions
#             options = ChromeOptions()
#             if headless:
#                 options.add_argument("--headless=new")  # or --headless for older versions
#             service = ChromeService(ChromeDriverManager().install())
#             driver = webdriver.Chrome(service=service, options=options)
#
#         else:
#             raise ValueError(f"Unsupported browser: {browser}")
#
#         driver.maximize_window()
#         logger.info(f"Started {browser} driver (headless={headless})")
#
#     except Exception as e:
#         logger.exception("Failed to start WebDriver.")
#         # If driver creation fails, make sure the fixture does NOT silently return None.
#         # Re-raise so pytest fails loudly and you see the cause.
#         raise
#
#     yield driver
#
#     if driver:
#         driver.quit()
#         logger.info("Driver quit.")

