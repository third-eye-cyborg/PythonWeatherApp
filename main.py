import requests
import pandas as pd
import pickle
import os
import base64
import googleapiclient.discovery
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow

class WeatherApp():
    def __init__(self, lat, lon):
        response = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&appid=YOURAPIKEY&units=imperial").json()

        responseData = pd.json_normalize(response, record_path="daily")
        print(type(responseData))
        responseData = responseData[1:2]
        responseData['pop'][1] = responseData['pop'][1] *100

        msg_text = f"Tomorrow will have a low of: {responseData['temp.min'][1]}°, a high of: {responseData['temp.max'][1]}°, and a {responseData['pop'][1]}% chance of precipitation."

        # set permissions
        SCOPES = ['https://www.googleapis.com/auth/gmail.send',
                  'https://www.googleapis.com/auth/gmail.modify']

        # set up credentials
        home_dir = os.path.expanduser('~')

        json_path = os.path.join(home_dir, 'Downloads', 'credentials.json')

        flow = InstalledAppFlow.from_client_secrets_file(json_path, SCOPES)

        creds = flow.run_local_server(port=0)

        pickle_path = os.path.join(home_dir, 'gmail.pickle')
        with open(pickle_path, 'wb') as token:
            pickle.dump(creds, token)

        home_dir = os.path.expanduser('~')
        pickle_path = os.path.join(home_dir, 'gmail.pickle')
        creds = pickle.load(open(pickle_path, 'rb'))

        # Build the service
        service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)

        # Create the message
        message = MIMEMultipart('alternative')
        message['Subject'] = "Tomorrow's daily weather alert"
        message['From'] = 'thirdeyecyborg@gmail.com'
        message['To'] = 'thirdeyecyborg@gmail.com'
        messagePlain = msg_text
        messageHtml = '<b>Weather Update!</b>'
        message.attach(MIMEText(messagePlain, 'plain'))
        message.attach(MIMEText(messageHtml, 'html'))
        raw = base64.urlsafe_b64encode(message.as_bytes())
        raw = raw.decode()
        body = {'raw': raw}

        message_first = body
        message_full = (
            service.users().messages().send(
                userId="me", body=message_first).execute())
        print('Message sent!')




WeatherApp(lat=42.937084, lon=-75.6107)