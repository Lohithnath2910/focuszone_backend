from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import os
import csv
import requests

app = FastAPI()

load_dotenv()

READ_API_KEY = os.getenv("THINGSPEAK_READ_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# basic structures for the thingspeak and feedback we recieve, Chirag , you can modify if you think we need extra data 
class SensorData(BaseModel):
    humidity: float
    temperature: float
    light: float
    noise: float

class FeedbackData(BaseModel):
    feedback: int

# Im checking whether the csv files exist or not here , you guys can remove it, if needed
if not os.path.exists('sensor_data.csv'):
    with open('sensor_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "temperature", "humidity", "light", "noise"])

if not os.path.exists("feedback.csv"):
    with open("feedback.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "productivity"])


#base
@app.get("/")
def check():
    return {"message": "API is working hehe!"}

#THIS BELOW ENDPOINT IF WE WANT TOT DIRECTLY GET DATA FROM SENSOR RATHER THAN PULLING FROM THINGSPEAK

# @app.post("/sensor-data")
# def recieve_sensor_data(data: SensorData):
    
#     global latest_data

#     timestamp = datetime.now()

#     latest_data = {
#         "timestamp": str(timestamp),
#         "temperature": data.temperature,
#         "humidity": data.humidity,
#         "light": data.light,
#         "noise": data.noise
#     }

#     with open('sensor_data.csv', 'a', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow([
#             timestamp, 
#             data.temperature, 
#             data.humidity,
#             data.light,
#             data.noise])
        
#     return {"message": "Stored successfully", "data": latest_data}


#ok so since we have the above json which we got, now ill just send it to flutter app , hope you understood that logic what i tried here

@app.get("/latest-data")
def get_latest_data():
    if 'latest_data' in globals():
        return latest_data
    else:
        return {"message": "No data received yet."}
    
#now to recive the feedback from the flutter app, and store it in a diff file (idk chirag , you just lemme know how you want to store it finally bro), for now imma keep it like this

@app.post("/feedback")
def recieve_feedback(data: FeedbackData):
    timestamp = datetime.now()

    with open("feedback.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, data.feedback])
        
    return {"message": "Feedback stored successfully", "data": {"timestamp": str(timestamp), "feedback": data.feedback}}


#func to pull from thing speak
def fetch_from_thingspeak():

    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results=1"

    response = requests.get(url)
    data = response.json()

    feeds = data.get("feeds", [])

    if not feeds:
        return None

    entry = feeds[0]

    return {
        "timestamp": entry["created_at"],
        "temperature": float(entry["field1"]),
        "humidity": float(entry["field2"]),
        "noise": float(entry["field3"]),
        "light": float(entry["field4"])
    }

@app.get("/thingspeak-data")
def get_thingspeak_data():
    global latest_data

    data = fetch_from_thingspeak()
    if not data:
        return {"message": "No data available from ThingSpeak."}
    latest_data = data
    with open('sensor_data.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            data["timestamp"],
            data["temperature"],
            data["humidity"],
            data["light"],
            data["noise"]
        ])

    return {"message": "Data pulled from ThingSpeak", "data": latest_data}