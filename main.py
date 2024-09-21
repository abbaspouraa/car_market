import re
import os
import json
from time import sleep

from selenium.common import NoSuchElementException

import google_chrom_driver
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

load_dotenv('.env')
user_name = os.getenv('USER_NAME')
password = os.getenv('PASSWORD')

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
    print("Logged in!")

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

def populate_data(car_data: dict):
    print("Populating initial data...")
    for car in car_data:
        for element in car_data[car]:
            url = element['url']
            try:
                details = extract_detail_info(url)
                element.update(details)
            except Exception as e:
                print(f"Error in fetching details for {url}")


def __clean_text(text: str):
    clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    clean = clean.replace("Joined Facebook in ", "")
    clean = clean.replace(" See less", "")
    return clean.replace("\n", " ").replace("  ", ". ")


def extract_detail_info(url: str) -> dict:
    driver.get(url)
    try:
        see_more = WebDriverWait(driver, 1).until(
            ec.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'See more')]"))
        )
        see_more.click()
    except:
        pass
    title_xpath = "/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div[1]/h1/span"
    title_xpath2 = "/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div[2]/div/div[1]/div[1]/div[2]/div[1]/h1/span"
    warning = False
    try:
        title_element = driver.find_element(By.XPATH, title_xpath)
    except NoSuchElementException:
        title_element = driver.find_element(By.XPATH, title_xpath2)
        warning = True
    update_info_element = title_element.find_element(By.XPATH, "../../following-sibling::div[2]/div/div/div/span/span")
    details_element = title_element.find_element(By.XPATH, "../../../following-sibling::div[4]/div[2]")
    description_element = title_element.find_element(By.XPATH, "../../../following-sibling::div[5]/div[2]/div/div/div/span")
    seller_name = title_element.find_element(By.XPATH, "../../../following-sibling::div[6]/div/div[2]//div/span")
    seller_year_joined = title_element.find_element(By.XPATH, "../../../following-sibling::div[6]/div/div[2]/div[last()]")

    first_image_xpath = "/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div[1]/div/div[3]/div/div[1]/div/div/img"
    images = []
    try:
        first_image_element = driver.find_element(By.XPATH, first_image_xpath)
        images.append(first_image_element.get_attribute('src'))
        parent_elements = first_image_element.find_elements(By.XPATH, "../../../following-sibling::* | ../../../preceding-sibling::*")
    except Exception as e:
        parent_elements = []
    for parent_element in parent_elements:
        image_element = parent_element.find_element(By.XPATH, ".//img")
        images.append(image_element.get_attribute('src'))
    output = {
        'updated': __clean_text(update_info_element.text),
        'details': re.split(r'\n|\u00b7', details_element.text),
        'description': __clean_text(description_element.text),
        'seller_name': __clean_text(seller_name.text),
        'seller_year_joined': __clean_text(seller_year_joined.text),
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




if __name__ == "__main__":
    print("Starting web scraping")
    login()
    interested_cars = ["Ford F150", "Toyota Tundra", "Nissan Titan", "Nissan Frontier", "Toyota Tacoma"]
    data = {}
    for car_name in interested_cars:
        result = search_cars(car_name)
        data[car_name] = result
        print(f"Collected initial data for {car_name}")

    populate_data(data)
    driver.quit()
    print("Storing data...")
    with open("output/data.json", 'w') as file:
        json.dump(data, file, indent=4)