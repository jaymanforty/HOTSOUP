import requests
import os
import datetime
from dotenv import load_dotenv 

load_dotenv()

API_KEY = os.getenv("NASA_API_KEY")
date = datetime.date.today()
r = requests.get(f'https://api.nasa.gov/planetary/apod?api_key={API_KEY}&date={date}').json()

#sometimes the APOD is a video instead of an HD picture
try:
    print(r['hdurl'])
except KeyError:
    print(r['url'])

print(r['explanation'])
print(r['date'])