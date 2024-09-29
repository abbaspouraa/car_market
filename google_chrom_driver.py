from selenium import webdriver

def get_driver() -> webdriver.Chrome:
    # Adding preferences to Chrome options
    options = webdriver.ChromeOptions()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument('--headless')  # Use '--headless' for standard headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    prefs = {
        "profile.managed_default_content_settings.images": 2,  # Disable images
        "profile.managed_default_content_settings.videos": 2,  # Disable videos
    }
    options.add_experimental_option("prefs", prefs)

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=options)
    return driver
