import os
import pickle
import platform

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ...settings import get_app_settings

config = get_app_settings()


# Singleton Pattern: https://stackoverflow.com/a/6798042
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        elif isinstance(cls._instances[cls], Browser):
            cls._instances[cls].__init__(browser = cls._instances[cls].browser, *args, **kwargs)
        return cls._instances[cls]

class Browser(metaclass = Singleton):

    def __init__(self, browser = None, google_login_flag = False):
        self.browser = browser

        if self.browser == None or not self.is_browser_reachable():
            os.system("taskkill /f /im chromedriver.exe")
            proxy = config.PROXY
            try:
                chrome_options = webdriver.ChromeOptions()
                if config.HEADLESS:
                    chrome_options.add_argument('--headless') # Runs Chrome in headless mode
                    # https://stackoverflow.com/a/53828727
                    chrome_options.add_argument('user-agent=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
                chrome_options.add_argument('--no-sandbox') # Bypass OS security model
                if platform.system() == 'Windows':
                    chrome_options.add_argument('--disable-gpu')  # applicable to windows os only
                chrome_options.add_argument('--start-maximized')
                chrome_options.add_argument('--incognito')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--disable-popup-blocking')
                chrome_options.add_argument('--disable-notifications')
                chrome_options.add_argument('--ignore-certificate-errors')
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                if proxy:
                    chrome_options.add_argument('--proxy-server = http://%s' % proxy)
                    self.browser = webdriver.Chrome(options = chrome_options, executable_path = chromedriver_autoinstaller.install())
                else:
                    self.browser = webdriver.Chrome(options = chrome_options, executable_path = chromedriver_autoinstaller.install())

                self.google_logged_in = False
                # Login to Google Account
                if google_login_flag:
                    self.google_logged_in = self.google_login()
            except Exception as e:
                print(e)

    def is_browser_reachable(self):
        try:
            self.browser.title
            return True
        except Exception as e:
            # Log message only if browser is not reachable
            if self.browser is not None:
                print(e)
                self.browser.quit()
                os.system("taskkill /f /im chromedriver.exe")
            return False

    def google_login(self):
        try:
            self.browser.get('https://mail.google.com')
            if ('inbox' in self.browser.title.lower()):
                self.google_logged_in = True
                print('Already logged into Google Account!')
                return True

            self.browser.get(config.GOOGLE_LOGIN_URL)
            username = os.environ['GOOGLE_USERNAME_ENV']
            password = os.environ['GOOGLE_PASSWORD_ENV']

            WebDriverWait(self.browser, 15).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='identifierId']"))).send_keys(username)
            self.browser.find_element_by_id("identifierNext").click()
            WebDriverWait(self.browser, 15).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='password']"))).send_keys(password)
            self.browser.find_element_by_id("passwordNext").click()
            self.google_logged_in = True
            print('Successfully logged into Google Account using credentials!')
            return True
        except Exception as e:
            print(e)
            return False
