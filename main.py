import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

# Create and configure the Chrome webdriver
url = "https://www.amazon.de/Playstation-1000040657-PlayStation%C2%AE5-Digital-Edition-Modellgruppe/dp/B0CLTBHXWQ/ref=sr_1_1?crid=OUO3FYQS1QIA&dib=eyJ2IjoiMSJ9.CtZVrA0ZzR8jzGvlA32tT8A2SKpb1ZMEce-cH9Os8GmiStxtpU3OXt9-KxTLoJAuPI_6wPnFH70WqIbwGAGLvV_D-LWyojcxcw1Ry83VceRvM1F8YitzPz9rGgODGp3EG_ctq0D-Ir-TEIevWlI9DMIcPmXQGANReIVllKFMyZyhZq16YN_YxVdKJfIbEvjEK0NvJLYQIf7XZRxpEZ93pjXJVxw8TuVyLfRtN4tsifI.7z9OiFsgmz1_C0AqCK7nec3ud8-TdKJ2BV_9R7I44EA&dib_tag=se&keywords=playstation%2B5&qid=1726596984&sprefix=pl%2Caps%2C138&sr=8-1&th=1"
#driver_path = '/path/to/chromedriver'
def get_product_info(url):

    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)

    time.sleep(2)
    try:

        title = driver.find_element(By.ID, "productTitle").text.strip()
    except:
        title = "No title"

    try:
        price = driver.find_element(By.CLASS_NAME, "a-price-whole").text.strip()
    except:
        price = "No price info"

    try:
        availability = driver.find_element(By.ID, "availability").text.strip()
    except:
        availability = "No more"

    driver.quit()
    return {
        "Title": title,
        "Price": price,
        "Availability": availability
    }


product_data = get_product_info(url)


def save_to_csv(data, filename="product_tracking.csv"):
    # Check if file exists and append, otherwise create a new file
    try:
        df_existing = pd.read_csv(filename)
    except FileNotFoundError:
        df_existing = pd.DataFrame()

    # Convert the dictionary into a DataFrame
    df_new = pd.DataFrame([data])

    # Append new data
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)

    # Save to CSV
    df_combined.to_csv(filename, index=False)

PRICE_THRESHOLD = 449

def check_price_drop(current_price_str, filename="product_tracking.csv"):
    # Convert the current price from string to float (assumes format '$999.99')
    current_price = float(current_price_str.replace('$', '').replace(',', ''))

    # Load existing CSV to check historical prices
    try:
        df = pd.read_csv(filename)
        last_price_str = df['Price'].iloc[-1].replace('$', '').replace(',', '')
        last_price = float(last_price_str)
    except (FileNotFoundError, IndexError):
        # If no data is found, treat it as the first run (no price history)
        last_price = current_price

    # Check if price has dropped
    if current_price < last_price or current_price < PRICE_THRESHOLD:
        send_price_alert(current_price)
    else:
        print(f"Price did not drop (Current: ${current_p
        rice}, Previous: ${last_price})")

def send_price_alert(current_price):
    # Email settings
    sender_email = "yourmail@gmail.com"
    receiver_email = "clientsmail@gmail.com"
    password = "yourpin"

    subject = f"Price Drop Alert: New Price is ${current_price}"
    body = f"The price of your tracked item has dropped to ${current_price}."

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Setup SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()  # Encrypt the connection
    server.login(sender_email, password)

    # Send the email
    server.sendmail(sender_email, receiver_email, msg.as_string())

    # Disconnect from the server
    server.quit()

    print(f"Price drop alert sent to {receiver_email}")

