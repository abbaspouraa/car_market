import re
import os
import json
from time import sleep
import google_chrom_driver
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv('.env')
user_name = os.getenv('USER_NAME')
password = os.getenv('PASSWORD')
CARS = os.getenv('CARS').split(";")

driver = google_chrom_driver.get_driver()

def login():
    login_url = 'https://www.facebook.com/'
    driver.get(login_url)

    driver.find_element(By.ID, 'email').send_keys(user_name)
    driver.find_element(By.ID, 'pass').send_keys(password)
    login_button = WebDriverWait(driver, 180).until(
        ec.element_to_be_clickable((By.NAME, 'login'))
    )
    login_button.click()
    print("[INFO] Logged in!")

def search_cars(car_name: str) -> list:
    sleep(2)
    search_link = 'https://www.facebook.com/marketplace/hamilton/search?query=' + car_name
    driver.get(search_link)
    driver.execute_script("return document.body.scrollHeight")

    items = []

    price_xpath = "//span[contains(text(), 'CA$')][1]"
    price_elements = driver.find_elements(By.XPATH, price_xpath)

    title_pattern = r'([\d]{4}) ([\w\d]*) ([\w\d-]*)?[\s]?([\d\w ]*)'

    for price_element in price_elements:
        try:
            price = price_element.text
            image_element = price_element.find_element(By.XPATH, "../../../../preceding-sibling::div//img")
            url = price_element.find_element(By.XPATH, "../../../../../../../a")
            title_element = price_element.find_element(By.XPATH, "../../../following-sibling::div[1]//span")
            location_element = price_element.find_element(By.XPATH, "../../../following-sibling::div[2]//span")
            distance_element = price_element.find_element(By.XPATH, "../../../following-sibling::div[3]//span")
            title = title_element.text
            match = re.search(title_pattern, title)

            item = {
                'price': price,
                'year': match.group(1),
                'make': match.group(2),
                'model': match.group(3),
                'location': location_element.text,
                'mileage': distance_element.text,
                'image': image_element.get_attribute('src'),
                'url': url.get_attribute('href')
            }
            # Only add trim if it's available
            if match.group(4):
                item['trim'] = match.group(4)
            items.append(item)
        except Exception as e:
            continue
    return items

def populate_data(car_data: dict) -> dict:
    global driver
    updated_data = {}
    print("[INFO] Populating initial data...")
    total = sum([len(item) for item in car_data.values()])
    cnt = 0
    for car in car_data:
        updated_data[car] = []
        for element in car_data[car]:
            url = element['url'].split("/?ref=")[0]
            try:
                cnt += 1
                print(f"\r[INFO] Extracting data from {url}. {cnt}/{total}", end='', flush=True)
                details = extract_detail_info(url)
                element.update(details)
                updated_data[car].append(element)
            except Exception as e:
                print(f"[ERROR] {type(e).__name__} Error in fetching details for {url}.")
                driver.quit()
                driver = google_chrom_driver.get_driver()
    return updated_data


def __clean_text(text: str):
    clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    clean = clean.replace("Joined Facebook in ", "")
    clean = clean.replace(" See less", "")
    return clean.replace("\n", " ").replace("  ", ". ")


def __click_see_more():
    see_mores = WebDriverWait(driver, 1).until(
        ec.presence_of_all_elements_located((By.XPATH, "//span[contains(text(), 'See more')]"))
    )
    for see_more in see_mores:
        try:
            see_more.click()
        except ElementClickInterceptedException:
            pass

def __close_login():
    xpath = "/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/i"
    log_in_box = WebDriverWait(driver, 1).until(
        ec.element_to_be_clickable((By.XPATH, xpath))
    )
    log_in_box.click()


def extract_detail_info(url: str) -> dict:
    driver.get(url)
    __close_login()
    __click_see_more()
    title_element, warning = get_title()
    update_info_element = title_element.find_element(By.XPATH, "../../following-sibling::div[2]/div/div/div/span/span")
    details_element = title_element.find_element(By.XPATH, "../../../following-sibling::div[4]/div[2]")
    try:
        description_element = title_element.find_element(By.XPATH, "../../../following-sibling::div[5]/div[2]/div/div/div/span")
        description = __clean_text(description_element.text)
    except NoSuchElementException:
        description = ""
    try:
        seller_name = title_element.find_element(By.XPATH, "../../../following-sibling::div[6]/div/div[2]//div/span").text
        seller_year_joined = title_element.find_element(By.XPATH, "../../../following-sibling::div[6]/div/div[2]/div[last()]").text
    except NoSuchElementException:
        seller_name = ""
        seller_year_joined = "0"

    first_image_xpath = "//div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div[1]/div/div[3]/div/div[1]/div/div/img"
    images = []
    try:
        first_image_element = driver.find_element(By.XPATH, first_image_xpath)
        images.append(first_image_element.get_attribute('src'))
        parent_elements = first_image_element.find_elements(By.XPATH, "../../../following-sibling::* | ../../../preceding-sibling::*")
    except NoSuchElementException:
        parent_elements = []
    for parent_element in parent_elements:
        image_element = parent_element.find_element(By.XPATH, ".//img")
        images.append(image_element.get_attribute('src'))
    output = {
        'updated': __clean_text(update_info_element.text),
        'details': re.split(r'\n|\u00b7', details_element.text),
        'description': description,
        'seller_name': __clean_text(seller_name),
        'seller_year_joined': __clean_text(seller_year_joined),
        'images': images,
        'warning': warning
    }
    transmission = re.findall(r'([\w]*) transmission', details_element.text)
    n_owner = re.findall(r'([\d+]*) owner', details_element.text)
    mileage = re.findall(r'Driven ([\d,]* km)', details_element.text)
    fuel = re.findall(r'Fuel type: ([\w]*)', details_element.text)
    exterior_color = re.findall(r'Exterior color: ([\w]*)', details_element.text)
    interior_color = re.findall(r'Interior color: ([\w]*)', details_element.text)
    engine_size = re.findall(r'Engine size: ([-\d.]* L)', details_element.text)
    horse_power = re.findall(r'Horsepower: ([\d.]* hp)', details_element.text)

    for name, element in zip([
        'transmission',
        'number_of_owner',
        'mileage',
        'fuel',
        'exterior_color',
        'interior_color',
        'engine_size',
        'horse_power'
    ], [
        transmission,
        n_owner,
        mileage,
        fuel,
        exterior_color,
        interior_color,
        engine_size,
        horse_power
    ]):
        if len(element) > 0 and '-' not in element[0]:
            output[name] = element[0]

    return output


def get_title():
    title_xpath = "//div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div[1]/h1/span"
    title_xpath2 = "//div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div[2]/div/div[1]/div[1]/div[2]/div[1]/h1/span"
    warning = False
    try:
        title_element = driver.find_element(By.XPATH, title_xpath)
    except NoSuchElementException:
        title_element = driver.find_element(By.XPATH, title_xpath2)
        warning = True
    return title_element, warning


def main():
    global driver
    print("[INFO] Starting web scraping")
    login()
    data = {}
    for car_name in CARS:
        result = search_cars(car_name)
        data[car_name] = result
        print(f"[INFO] Collected initial data for {car_name}")

    driver.quit()
    driver = google_chrom_driver.get_driver()
    data = populate_data(data)
    driver.quit()
    print("[INFO] Storing data...")
    with open("output/data.json", 'w') as file:
        json.dump(data, file, indent=4)



if __name__ == "__main__":
    main()