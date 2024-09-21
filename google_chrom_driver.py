from selenium import webdriver
import undetected_chromedriver as uc

def get_driver() -> webdriver.Chrome:
    # Initialize Chrome options
    prefs = {
        'profile.managed_default_content_settings.images': 2,
        'disk-cache-size': 4096
    }

    # Adding preferences to Chrome options
    options = webdriver.ChromeOptions()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    options.add_experimental_option('prefs', prefs)

    # Initialize the WebDriver with the ChromeDriverManager
    return uc.Chrome(version_main=127)