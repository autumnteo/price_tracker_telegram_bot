from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import os
import requests
import datetime
import pytz


def lambda_handler(event, context):
    print("Starting to scrape")

    # set up environment variables
    TOKEN = os.environ["TELEGRAM_TOKEN"]
    CHAT_ID = os.environ["CHAT_ID"]
    URL = "https://www.amazon.com/Nintendo-32GB-Switch-Gray-Controllers/dp/B07YFKM7N6/ref=sr_1_14?dchild=1&keywords=switch&qid=1596442560&sr=8-14"
    TARGET_PRICE = 400

    # set up selenium options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280x1696')
    chrome_options.add_argument('--user-data-dir=/tmp/user-data')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--v=99')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--data-path=/tmp/data-path')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--homedir=/tmp')
    chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
    chrome_options.binary_location = os.getcwd() + "/bin/headless-chromium"

    driver = webdriver.Chrome(chrome_options=chrome_options)

    # functiont to get the current time of your timezone
    def getDateTime():
        dateTime = datetime.datetime.now()
        timeZone = pytz.timezone("Singapore")
        dateTime_aware = timeZone.localize(dateTime)
        hour_min = dateTime_aware.strftime(
            "%H:%M")
        return hour_min

    hour_min = getDateTime().split(":")
    hour = int(hour_min[0])
    minute = int(hour_min[1])

    prev_price = ""
    response = ""
    try:
        driver.get(URL)
        # get the previous price, discount price and total savings
        try:
            prev_price = WebDriverWait(driver, 10).until(
                presence_of_element_located((By.XPATH, "//*[@id='price']/table/tbody/tr[1]/td[2]/span[1]")))
            prev_price = prev_price.text.strip(" ")
            response += f'Original Price: {prev_price}.\n'
        except:
            pass

        try:
            curr_price = WebDriverWait(driver, 10).until(
                presence_of_element_located((By.ID, "priceblock_ourprice_row")))
            prices = curr_price.text.split(' ')
            base = round(float(prices[1][1:]), 2)
            shipping = round(float(prices[3][1:]), 2)

            # if there is no sale, the xpath will return the current base price, so there will be duplicate
            if (str(prev_price)[1:] == str(base)):
                response = ""
            response += f'Current Price: ${base} + ${shipping} shipping (Total: ${base+shipping})\n'
        except:
            pass

        try:
            savings = WebDriverWait(driver, 10).until(
                presence_of_element_located((By.CLASS_NAME, "priceBlockSavingsString")))
            savings = savings.text.strip(" ")
            response += f'Savings: {savings}.\n'
        except:
            pass

        print(hour, minute)
        # if total price is below the max you're willing to pay (i.e. have big discount), send a tele msg to u
        if (base+shipping) < TARGET_PRICE:
            response = f'The current price is below your ${TARGET_PRICE} Target!!!\n' + response
        # send a daily msg at 12 noon of the current price (i.e. a sanity check that the bot is still working)
        # hour == 4 because aws lambda is in UTC and singapore is UTC+8, so 12-8 = 4
        elif hour == 4 and (minute >= 0 and minute < 1):
            response = f'This is your daily price check\n' + response

    except Exception as e:
        response = f"Something went wrong with the bot\nError: {e}"

    finally:
        driver.close()
        driver.quit()

    TELEGRAM_SEND_MSG = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

    # only send the telegram msg if a) there is a big sale or b) when its noon
    if response.startswith("The current price") or response.startswith("This is your daily"):
        response += f'{URL}'
        data = {
            'chat_id': CHAT_ID,
            'text': response,
            'parse_mode': 'Markdown'
        }
        requests.post(TELEGRAM_SEND_MSG, data=data)

    return response
    # return None
