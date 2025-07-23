import pyttsx3
from datetime import datetime, timedelta
import time
from playsound import playsound
import speech_recognition as sr
import threading
import os
import eel

# Initialize the text-to-speech engine
engine = pyttsx3.init()

def play_alarm_sound():
    """Play the alarm sound"""
    alarm_sound_file = 'D:\\pytho\\jarvis\\www\\assets\\audio\\alarm.mp3'  # Ensure this path exists
    if not os.path.isfile(alarm_sound_file):
        print(f"Alarm sound file does not exist: {alarm_sound_file}")
        return
    
    try:
        playsound(alarm_sound_file)
    except Exception as e:
        print(f"Error playing alarm sound: {e}")
    
    
def set_alarm(alarm_time):
    """Set an alarm that will sound at the specified time"""
    while True:
        now = datetime.now()
        if now >= alarm_time:
            engine.say("Alarm! Wake up!")
            engine.runAndWait()
            play_alarm_sound()
            break
        time.sleep(1)

def recognize_voice():
    """Recognize input from voice and return it in lowercase"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        print("Recognizing...")
        try:
            text = recognizer.recognize_google(audio)
            text = text.lower().strip()  # Convert to lowercase and remove extra whitespace
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            print("Sorry, there was an error with the speech recognition service.")
            return None
def speak(text: str) -> None:
    """Function to speak out the given text."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def convert_to_hhmm(time_str):
    """Convert a string like 'HHMM' to 'HH:MM' format"""
    time_str = time_str.strip()
    if len(time_str) == 4 and time_str.isdigit():
        hours = int(time_str[:2])
        minutes = time_str[2:]
        if 0 <= hours < 24 and 0 <= int(minutes) < 60:
            return f"{hours:02}:{minutes}"
        else:
            return None
    else:
        return None

def alarm():
    method = None
    while method not in ['set my speak', 'text']:
        # Ask user for input method
        eel.DisplayMessage("Would you like to set the alarm orally or by text? Say 'set my speak' or 'text'.")
        engine.say("Would you like to set the alarm orally or by text? Say 'set my speak' or 'text'.")
        engine.runAndWait()
        print("Would you like to set the alarm orally or by text? Say 'set my speak' or 'text': ")
        method = recognize_voice()

        if method not in ['set my speak', 'text']:
            engine.say("Invalid choice. Please say 'set my speak' or 'text'.")
            engine.runAndWait()
            print("Invalid choice. Please say 'set my speak' or 'text'.")

    if method == 'set my speak':
        while True:
            eel.DisplayMessage("Please speak the alarm time in the format 'HHMM'.")
            speak("Please speak the alarm time in the format 'HHMM'.")
            alarm_time_str = recognize_voice()
            if alarm_time_str:
                alarm_time_str = convert_to_hhmm(alarm_time_str)
                if alarm_time_str:
                    try:
                        # Parse the user input into a datetime object
                        alarm_time = datetime.strptime(alarm_time_str, "%H:%M")
                        # Set the alarm for today
                        alarm_time = datetime.now().replace(hour=alarm_time.hour, minute=alarm_time.minute, second=0, microsecond=0)
                        # If the alarm time has already passed today, set it for the next day
                        if alarm_time < datetime.now():
                            alarm_time += timedelta(days=1)
                        speak(f"Alarm set for {alarm_time.strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"Alarm set for {alarm_time.strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        # Start the alarm in a separate thread
                        alarm_thread = threading.Thread(target=set_alarm, args=(alarm_time,))
                        alarm_thread.start()
                        break
                    except ValueError:
                        engine.say("Invalid time format. Please try again. The format should be 'HHMM'.")
                        engine.runAndWait()
                        print("Invalid time format. Please try again.")
                else:
                    engine.say("Invalid time provided. Please try again.")
                    engine.runAndWait()

    elif method == 'text':
        print("Please enter the alarm time in the format 'HH:MM' (24-hour format): ")
        alarm_time_str = input().strip()
        try:
            # Parse the user input into a datetime object
            alarm_time = datetime.strptime(alarm_time_str, "%H:%M")
            # Set the alarm for today
            alarm_time = datetime.now().replace(hour=alarm_time.hour, minute=alarm_time.minute, second=0, microsecond=0)
            # If the alarm time has already passed today, set it for the next day
            if alarm_time < datetime.now():
                alarm_time += timedelta(days=1)
            
            print(f"Alarm set for {alarm_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Start the alarm in a separate thread
            alarm_thread = threading.Thread(target=set_alarm, args=(alarm_time,))
            alarm_thread.start()
        except ValueError:
            print("Invalid time format. Please use 'HH:MM'.")

if __name__ == "__main__":
    # Start the alarm setting function
    alarm_thread = threading.Thread(target=alarm)
    alarm_thread.start()

    # Additional commands can be processed here while the alarm thread is running
    while True:
        command = recognize_voice()
        if command:
            print(f"Command recognized: {command}")
            if "exit" in command:
                print("Exiting...")
                break
        time.sleep(1)
