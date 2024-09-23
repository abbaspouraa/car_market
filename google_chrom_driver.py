from selenium import webdriver
import undetected_chromedriver as uc

def get_driver() -> webdriver.Chrome:
    # Adding preferences to Chrome options
    options = webdriver.ChromeOptions()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    # Initialize the WebDriver with the ChromeDriverManager
    return uc.Chrome(options=options, version_main=127)