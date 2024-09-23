import os
import pymysql
import google_chrom_driver
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException

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


if __name__ == '__main__':
    print("[INFO] Identifying sold cars...")
    sold_ids = identify_sold_cars()
    driver.quit()
    print("[INFO] Sold cars are identified.")
    update_db(sold_ids)
    print("[INFO] DB is updated.")