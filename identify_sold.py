import os
import pymysql
import requests
import google_chrom_driver
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv('.env')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')

connection = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, database='CarMarket', connect_timeout=5)
driver = google_chrom_driver.get_driver()

sql_identify_unsold_cars = """
SELECT url_id FROM CarWarehouse
WHERE sold = FALSE
"""

sql_mark_sold = """
UPDATE CarWarehouse
SET sold = TRUE
WHERE url_id = %s
"""

sql_all_images = """
SELECT id, imageUrl FROM CarImage
"""

sql_delete_images = """
DELETE FROM CarImage
WHERE id = %s
"""


url_prefix = "https://www.facebook.com/marketplace/item/"

def is_car_sold(url_id: int) -> bool:
    try:
        driver.get(url_prefix + str(url_id))
        title_element_xpath = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div[1]"
        title_element = driver.find_element(By.XPATH, title_element_xpath)
        title_text = title_element.text.lower()
        return 'sold' in title_text
    except NoSuchElementException:
        if str(url_id) in driver.current_url:
            return is_car_sold(url_id)
        return True


def identify_sold_cars():
    sold_url_ids = []
    url_ids = []
    with connection.cursor() as cursor:
        cursor.execute(sql_identify_unsold_cars)
        for row in cursor.fetchall():
            url_ids.append(row[0])

    for url_id in url_ids:
        if is_car_sold(url_id):
            sold_url_ids.append(url_id)

    return sold_url_ids



def update_db(sold_cars: list):
    with connection.cursor() as cursor:
        cursor.executemany(sql_mark_sold, sold_cars)
        connection.commit()

    connection.close()


def check_image_status(row):
    image_id, url = row[0], row[1]
    try:
        response = requests.get(url, timeout=10)  # Set a timeout to avoid long delays
        if response.status_code != 200:
            return image_id
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return image_id
    return None  # Return None if the image is present


def remove_missing_image_rows():
    print("[INFO] Fetching image rows.")
    image_ids = []

    # Fetch all image rows from the database
    with connection.cursor() as cursor:
        cursor.execute(sql_all_images)
        rows = cursor.fetchall()

    print("[INFO] Identifying missing images.")

    # Use ThreadPoolExecutor for multithreading
    with ThreadPoolExecutor(max_workers=12) as executor:
        future_to_row = {executor.submit(check_image_status, row): row for row in rows}

        # Process completed futures
        for future in as_completed(future_to_row):
            result = future.result()
            if result:  # If the result is an image_id of a missing image
                image_ids.append(result)

    print("[INFO] Removing missing images from database.")
    if image_ids:
        with connection.cursor() as cursor:
            cursor.executemany(sql_delete_images, [(image_id,) for image_id in image_ids])
        connection.commit()
        print("[INFO] Finished deleting missing images.")
    else:
        print("[INFO] No missing images found.")



if __name__ == '__main__':
    print("[INFO] Identifying sold cars...")
    sold_ids = identify_sold_cars()
    driver.quit()
    print("[INFO] Sold cars are identified.")
    update_db(sold_ids)
    print("[INFO] DB is updated.")
    remove_missing_image_rows()