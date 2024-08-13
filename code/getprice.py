from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import datetime
from tinyflux import TinyFlux
from tinyflux import Point
import os
import logging

BASE_URL = os.getenv('BASE_URL')
COOKIES_XPATH = os.getenv('COOKIES_XPATH')
PRICE_XPATH = os.getenv('PRICE_XPATH')
NUM_LINES_TO_READ = int(os.getenv('NUM_LINES_TO_READ'))
LIST_REFERENCES = os.getenv('LIST_REFERENCES')
CONTAINER_NAME = os.getenv('CONTAINER_NAME')

#link the tinyflux file in volume
tinyflux_file = "/app/data/" + CONTAINER_NAME + ".db"
db = TinyFlux(tinyflux_file)

#log 
log_file = "/app/data/logs/log_"+CONTAINER_NAME+".txt"
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename=log_file, level=logging.DEBUG)

#set chrome options
chrome_driver_binary = '/root/chromedriver'  #path to driver binary
options = webdriver.ChromeOptions()
options.binary_location = "/opt/google/chrome/chrome" #path to chrome binary
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")
options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
options.add_argument("--disable-dev-shm-usage") # avoid chrome to crash because of low memory
options.add_argument("--remote-debugging-port=9222") #solve ERROR : session not created: DevToolsActivePort file doesn't exist
options.add_argument("--no-sandbox") #solve : Webdriver exception: "chrome not reachable"
sleep(5)

# Extract container number from container name
container_index = int(CONTAINER_NAME.split("_")[1])

# Calculate starting index for reading lines
start_index = int(container_index * NUM_LINES_TO_READ)

# Initialize a list to store selected lines
ref = []

# Open the file and read line by line
with open(LIST_REFERENCES, 'r') as file:
    for _ in range(start_index):
        try:
            next(file)
        except StopIteration:
            # If start_index is beyond the end of the file, exit the loop
            break
    
    # Read and process the next NUM_LINES_TO_READ lines
    for _ in range(NUM_LINES_TO_READ):
        try:
            line = next(file).strip()
            ref.append(line)
        except StopIteration:
            # If there are no more lines in the file, exit the loop
            break

for row in ref:

    #base URL for Vuitton website
    url = BASE_URL+row

    #write url in log file
    logger.debug('url of %s is %s', row, url)

    # Launch a Chrome browser instance
    driver = webdriver.Chrome(chrome_driver_binary, chrome_options=options)
    driver.get(url)
    sleep(10)

    # accept cookies if banner is present
    cookies_banner = driver.find_elements(By.XPATH, COOKIES_XPATH)
    if cookies_banner:
        cookies_banner[0].click()
        sleep(5)

    try:
        # get price filed in web page
        link = driver.find_element(By.XPATH, PRICE_XPATH)

        text = link.get_attribute("innerText")
        timestamp = datetime.datetime.today()

        # Check if text is not empty
        if text:
            # Remove any whitespace, euro sign, and thousand separators
            numeric_string = text.replace(" ", "").replace("€", "").replace("*", "").replace(",", ".").replace("\xa0", "").replace("EUR", "")
            try:
                numeric_price = float(numeric_string)
                # Create a new entry for the database
                point = Point(
                    time=timestamp,
                    measurement='price',
                    tags={'bag': row, 'zone': "euro"},
                    fields={'count': numeric_price}
                )
                db.insert(point)
                # Write price in log file
                logger.info('price of %s is %s', row, str(numeric_price))
            except ValueError:
                # Handle the case where the numeric string cannot be converted to float
                logger.error('ERROR (Invalid price format) %s : %s', row, numeric_string)
        else:
            # Handle the case where text is empty
            logger.error('ERROR (No text found): %s', row)
        
    except NoSuchElementException:
        logger.error('ERROR (NoSuchElementException) : %s', row)

    with open(log_file, 'r') as log_file_to_docker:
            print(log_file_to_docker.read())

    driver.quit() #when in container, solve : failed to check if window was closed: disconnected: not connected to DevTools