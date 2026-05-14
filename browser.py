import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import config


class BrowserManager:
    def __init__(self):
        self.driver = None
        self.wait = None

    def start(self):
        chrome_options = Options()
        if config.HEADLESS:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, config.TIMEOUT)
        return self

    def get(self, url):
        self.driver.get(url)
        time.sleep(2)

    def find_element(self, by, value):
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def find_elements(self, by, value):
        return self.driver.find_elements(by, value)

    def click(self, by, value):
        element = self.find_element(by, value)
        element.click()
        time.sleep(1)

    def send_keys(self, by, value, text):
        element = self.find_element(by, value)
        element.clear()
        element.send_keys(text)
        time.sleep(0.5)

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    def scroll_to_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)

    def get_page_source(self):
        return self.driver.page_source

    def execute_script(self, script, *args):
        return self.driver.execute_script(script, *args)

    def close(self):
        if self.driver:
            self.driver.quit()

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
