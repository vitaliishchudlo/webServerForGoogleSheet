import time

from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from app_loger import AppLogger
import time
from logging import getLogger


app = Flask(__name__)
logger = getLogger('AppLogger')

LINK_PREFIX = 'api_v1/for-csgo-google-sheet'
NEEDED_ARGUMENT_IN_LINK = 'skin_name'


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.headless = False
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


@app.route('/')
def index():
    logger.info('I am in the route: /')
    if not request.args.get(NEEDED_ARGUMENT_IN_LINK):
        logger.info(f'Returning error, because bad {NEEDED_ARGUMENT_IN_LINK}')
        return jsonify(error=f"You must specify a '{NEEDED_ARGUMENT_IN_LINK}' parameter in the link")

    skin_name = request.args.get(NEEDED_ARGUMENT_IN_LINK)
    skin_name = skin_name.replace(' ', '%20')

    skin_link = f'https://steamcommunity.com/market/listings/730/{skin_name}'
    logger.info(f'Link created -> {skin_link}')

    driver = create_driver()
    logger.info(f'Driver created -> {driver}')
    try:
        logger.info('Trying to open link')
        driver.get(skin_link)
        element_name = driver.find_element(By.ID, 'largeiteminfo_item_name')
        name_of_skin_text = element_name.text
        logger.info(f'Name of skin text -> {name_of_skin_text}')

        element_of_sales = driver.find_element(By.CLASS_NAME, 'market_commodity_order_summary')
        driver.execute_script("arguments[0].scrollIntoView();", element_of_sales)
        time.sleep(1)

        try:
            lowest_price_text = element_of_sales.text.split('$')[-1]
            count_of_sales_text = element_of_sales.text.split(' ')[0]
        except Exception:
            driver.refresh()
            time.sleep(3)
            driver.execute_script("arguments[0].scrollIntoView();", element_of_sales)
            time.sleep(1)
            lowest_price_text = element_of_sales.text.split('$')[-1]
            count_of_sales_text = element_of_sales.text.split(' ')[0]

        return jsonify(title_of_skin=name_of_skin_text, lowest_price=lowest_price_text,
                       count_of_sales=count_of_sales_text)
    except Exception as err:
        return jsonify(title='Error', skin_link=skin_link, traceback=err)
    finally:
        driver.quit()


if __name__ == '__main__':
    AppLogger()
    app.run()
