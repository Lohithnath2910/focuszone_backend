import requests
import random
import time
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv()

WRITE_API_KEY = os.getenv("THINGSPEAK_WRITE_API_KEY")
URL = os.getenv("THINGSPEAK_URL")


while True:

    temperature = round(random.uniform(24, 36), 2)
    humidity = round(random.uniform(35, 85), 2)
    noise = random.randint(30, 90)              
    light_intensity = random.randint(100, 1000)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payload = {
        "api_key": WRITE_API_KEY,
        "field1": temperature,
        "field2": humidity,
        "field3": noise,
        "field4": light_intensity,
        "field5": timestamp
    }

    try:
        response = requests.post(URL, data=payload)

        print("Sent Data:")
        print(payload)
        print("ThingSpeak Response:", response.text)
        print("-" * 40)

    except Exception as e:
        print("Error:", e)


    time.sleep(20)