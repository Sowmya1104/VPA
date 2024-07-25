import speech_recognition as sr
import pyttsx3
import wikipedia
import webbrowser
import os
import smtplib
import imaplib
import email
import requests
import pyowm
from datetime import datetime, timedelta
import time
import schedule

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
            return query.lower()
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that. Please say that again.")
            return None
        except sr.RequestError:
            speak("Sorry, my speech service is down. Please try again later.")
            return None

def open_website(url):
    speak(f"Opening {url}")
    webbrowser.open(f"http://{url}")

def open_file(file_path):
    speak(f"Opening file {file_path}")
    os.startfile(file_path)

def send_email(to, subject, body):
    user = 'your_email@gmail.com'
    password = 'your_password'
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user, password)
        message = f'Subject: {subject}\n\n{body}'
        server.sendmail(user, to, message)
        server.quit()
        speak('Email has been sent!')
    except Exception as e:
        speak('Sorry, I am unable to send the email at the moment.')

def read_emails():
    user = 'your_email@gmail.com'
    password = 'your_password'
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(user, password)
        mail.select('inbox')
        _, search_data = mail.search(None, 'UNSEEN')
        for num in search_data[0].split():
            _, data = mail.fetch(num, '(RFC822)')
            _, b = data[0]
            msg = email.message_from_bytes(b)
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True)
                    speak(body.decode())
        mail.logout()
    except Exception as e:
        speak('Sorry, I am unable to read emails at the moment.')

def get_weather(city):
    api_key = "your_openweather_api_key"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + api_key + "&q=" + city
    response = requests.get(complete_url)
    data = response.json()
    if data["cod"] != "404":
        main = data["main"]
        weather_desc = data["weather"][0]["description"]
        temperature = main["temp"] - 273.15  # Convert from Kelvin to Celsius
        speak(f"The temperature in {city} is {temperature:.2f} degrees Celsius with {weather_desc}.")
    else:
        speak("City not found.")

def check_trigger():
    api_key = "your_openweather_api_key"
    location = "Chirala,IN"
    complete_url = f"http://api.openweathermap.org/data/2.5/weather?lat=15.82&lon=80.36&appid={api_key}"
    response = requests.get(complete_url)
    data = response.json()
    if data["cod"] != "404":
        main = data["main"]
        temperature = main["temp"] - 273.15  # Convert from Kelvin to Celsius
        if temperature < 0:
            speak("Alert! The air temperature in Chirala has fallen below 0°C.")
    else:
        speak("Error checking weather conditions.")

def set_reminder(reminder_time, message):
    with open('reminders.txt', 'a') as file:
        file.write(f"{reminder_time} - {message}\n")
    speak(f"Reminder set for {reminder_time} with message: {message}")

def check_reminders():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('reminders.txt', 'r') as file:
        lines = file.readlines()
    with open('reminders.txt', 'w') as file:
        for line in lines:
            reminder_time, message = line.strip().split(' - ')
            if reminder_time <= current_time:
                speak(f"Reminder: {message}")
            else:
                file.write(line)

def play_music():
    music_dir = 'path_to_your_music_directory'
    songs = os.listdir(music_dir)
    os.startfile(os.path.join(music_dir, songs[0]))

def process_command(command):
    if 'wikipedia' in command:
        speak('Searching Wikipedia...')
        command = command.replace('wikipedia', '')
        results = wikipedia.summary(command, sentences=2)
        speak("According to Wikipedia")
        speak(results)
    elif 'open website' in command or 'open' in command:
        command = command.replace('open website', '').replace('open', '').strip()
        if command:
            open_website(command)
    elif 'open file' in command:
        speak('Which file would you like to open? Please provide the full file path.')
        command = listen()
        if command:
            open_file(command)
    elif 'send email' in command:
        speak('To whom should I send the email?')
        to = listen()
        speak('What is the subject?')
        subject = listen()
        speak('What should be the body of the email?')
        body = listen()
        if to and subject and body:
            send_email(to, subject, body)
    elif 'read emails' in command:
        read_emails()
    elif 'weather in' in command:
        city = command.replace('weather in', '').strip()
        get_weather(city)
    elif 'set reminder' in command:
        speak('When should I remind you? Please provide the time in YYYY-MM-DD HH:MM:SS format.')
        reminder_time = listen()
        speak('What should I remind you about?')
        message = listen()
        if reminder_time and message:
            set_reminder(reminder_time, message)
    elif 'play music' in command:
        play_music()
    elif 'stop' in command:
        speak("Goodbye!")
        return False
    return True

def main():
    speak("Hello, I am your virtual assistant. How can I help you today?")
    schedule.every().hour.do(check_trigger)
    schedule.every(1).minutes.do(check_reminders)
    while True:
        schedule.run_pending()
        command = listen()
        if command:
            if not process_command(command):
                break

if __name__ == "__main__":
    main()
