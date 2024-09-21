import re
import os
import json
import pymysql
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv('.env')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')

connection = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, database='CarMarket', connect_timeout=5)

sql_insert_query_cw = """
INSERT INTO CarWarehouse (price, year, make, model, trim, location, mileage, image, url_id, last_update, 
description, seller_name, seller_year_joined, warning, transmission, fuel, exterior_color, interior_color, horse_power,
engine_size, number_of_owner) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
ON DUPLICATE KEY UPDATE 
price = VALUES(price),
year = VALUES(year),
make = VALUES(make),
model = VALUES(model),
trim = VALUES(trim),
location = VALUES(location),
mileage = VALUES(mileage),
image = VALUES(image),
last_update = VALUES(last_update),
description = VALUES(description),
seller_name = VALUES(seller_name),
seller_year_joined = VALUES(seller_year_joined),
warning = VALUES(warning),
transmission = VALUES(transmission),
fuel = VALUES(fuel),
exterior_color = VALUES(exterior_color),
interior_color = VALUES(interior_color),
horse_power = VALUES(horse_power),
engine_size = VALUES(engine_size),
number_of_owner = VALUES(number_of_owner)
"""

sql_insert_query_ci = """
INSERT INTO CarImage (car_url_id, imageUrl) 
VALUES (%s, %s)
ON DUPLICATE KEY UPDATE imageUrl = VALUES(imageUrl);
"""

def __extract_number(text: str, integer: bool = True):
    clean = re.sub(r'[^0-9.]', '', text)
    if integer:
        return int(clean)
    return Decimal(clean)

def __extract_id(text: str) -> int:
    value = re.search(r'/item/(\d+)/', text)
    return int(value.group(1))

def insert_image_data(url_id_list: list, images_list: list):
    rows = []
    for url_id, images in zip(url_id_list, images_list):
        for image in images:
            rows.append((url_id, image))

    try:
        with connection.cursor() as cursor:
            cursor.executemany(sql_insert_query_ci, rows)
            print("Image data is stored.")
    except Exception as e:
        print(f"ERROR in insert image data: {e}")
        exit(1)


def load_json_file_into_db():
    with open('output/data.json', 'r') as file:
        car_data = json.load(file)
    rows = []
    url_list = []
    images_list = []

    for search_name in car_data:
        for car in car_data[search_name]:
            price_value = __extract_number(car['price'])
            year_value = __extract_number(car['year'])
            make_value = car['make']
            model_value = car['model']
            trim_value = car['trim'] if 'trim' in car else ''
            location_value = car['location']
            mileage_value = __extract_number(car['mileage'])
            image_value = car['image']
            url_value = __extract_id(car['url'])
            last_update_value = car['updated']
            description_value = car['description']
            seller_name_value = car['seller_name']
            seller_year_joined_value = car['seller_year_joined']
            warning_value = bool(car['warning'])
            transmission_value = car['transmission'] if 'transmission' in car else ''
            fuel_value = car['fuel'] if 'fuel' in car else ''
            exterior_color_value = car['exterior_color'] if 'exterior_color' in car else ''
            interior_color_value = car['interior_color'] if 'interior_color' in car else ''
            horse_power_value = __extract_number(car['horse_power'] if 'horse_power' in car else "0")
            engine_size_value = __extract_number(car['engine_size'] if 'engine_size' in car else "1.0", False)
            number_of_owner_value = car['number_of_owner'] if 'number_of_owner' in car else "?"

            rows.append((price_value, year_value, make_value, model_value, trim_value, location_value,
                         mileage_value, image_value, url_value, last_update_value, description_value,
                         seller_name_value, seller_year_joined_value, warning_value, transmission_value,
                         fuel_value, exterior_color_value, interior_color_value,
                         horse_power_value, engine_size_value, number_of_owner_value))
            images_list.append(car['images'])
            url_list.append(url_value)

    try:
        with connection.cursor() as cursor:
            cursor.executemany(sql_insert_query_cw, rows)

        insert_image_data(url_list, images_list)
        connection.commit()
        os.remove('output/data.json')
    except Exception as e:
        print(f"ERROR in insert car data: {e}")
    finally:
        connection.close()

if __name__ == '__main__':
    print("Storing data into MySQL DB")
    load_json_file_into_db()
    print("All data is stored in MySQL DB.")
