import os
import pymysql
import gmail_script
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

load_dotenv('.env')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
EMAIL = os.getenv('EMAIL')
SUBJECT = os.getenv('SUBJECT')

connection = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, database='CarMarket', connect_timeout=5)

sql_car = """
SELECT price, year, make, model, trim, location, mileage, url_id, last_update, description, seller_name, seller_year_joined,
 number_of_owner, createdAt, updatedAt FROM CarWarehouse
WHERE url_id = %s
"""

sql_images = """
SELECT imageUrl FROM CarImage
WHERE car_url_id = %s
"""

sql_find_cars = """
SELECT DISTINCT url_id FROM CarWarehouse
WHERE createdAt BETWEEN NOW() - INTERVAL 30 MINUTE AND NOW()
AND year > 2010
AND price < 16000
AND price > 2000
AND mileage < 200000
AND mileage > 70000
"""

def get_car_data(url_id: int) -> dict:
    with connection.cursor() as cursor:
        cursor.execute(sql_car, url_id)
        car_data = cursor.fetchall()[0]

    with connection.cursor() as cursor:
        cursor.execute(sql_images, url_id)
        images = cursor.fetchall()

    return {
        "price": car_data[0],
        "year": car_data[1],
        "make": car_data[2],
        "model": car_data[3],
        "trim": car_data[4],
        "location": car_data[5],
        "mileage": car_data[6],
        "images": [image[0] for image in images],
        "link": f"https://www.facebook.com/marketplace/item/{car_data[7]}",
        "last_update": car_data[8],
        "description": car_data[9].lower(),
        "seller_name": car_data[10],
        "seller_year_joined": car_data[11],
        "num_owners": car_data[12],
        "created_at": str(car_data[13]),
        "updated_at": str(car_data[14]),
    }

def render_email_template(template_name, context):
    template_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)
    return template.render(context)


def send_email():
    context = {
        "cars": []
    }

    print("[INFO] Collecting good cars.")
    with connection.cursor() as cursor:
        cursor.execute(sql_find_cars)
        car_ids = cursor.fetchall()

    if len(car_ids) == 0:
        print("[INFO] No cars found")
        return

    print("[INFO] Fetching car details.")
    for car_id in car_ids:
        car_data = get_car_data(car_id[0])
        context['cars'].append(car_data)


    print("[INFO] Sending email.")
    email_content = render_email_template("email_template.html", context)
    gmail_script.send_email(EMAIL, email_content, SUBJECT)
    print("[INFO] Email sent")


if __name__ == '__main__':
    send_email()
