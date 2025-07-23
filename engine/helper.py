import os
import re
import time
import psutil
import pyautogui
import pyttsx3
def extract_yt_term(command):
    # Define a regular expression pattern to capture the song name
    pattern = r'play\s+(.*?)\s+on\s+youtube'
    # Use re.search to find the match in the command
    match = re.search(pattern, command, re.IGNORECASE)
    # If a match is found, return the extracted song name; otherwise, return None
    return match.group(1) if match else None
def speak(self, text, language='en'):
        try:
            engine = pyttsx3.init('sapi5')
            voices = engine.getProperty('voices') 
            engine.setProperty('voice', voices[0].id)
            engine.setProperty('rate', 174)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Error in speak function: {e}")
def extract_ig_term(query):
    # Define a list of keywords or phrases to remove
    keywords = ['play', 'instagram', 'reels', 'search', 'on']
    # Clean up the query string by removing specified keywords
    search_term = remove_words(query, keywords)
    return search_term

def remove_words(input_string, words_to_remove):
    # Convert the list of words to remove into lowercase for case-insensitive comparison
    words_to_remove = set(word.lower() for word in words_to_remove)
    
    # Split the input string into words
    words = input_string.split()
    
    # Remove unwanted words while preserving their original case
    filtered_words = [word for word in words if word.lower() not in words_to_remove]
    
    # Join the remaining words back into a string
    result_string = ' '.join(filtered_words)
    
    return result_string
def cpu() -> None:
    """Function to report CPU usage and battery status."""
    usage = psutil.cpu_percent()
    speak(f"CPU usage is at {usage}%")

    battery = psutil.sensors_battery()
    if battery:
        speak(f"Battery is at {battery.percent}%")
    else:
        speak("Battery status not available.")
def screenshot(save_path: str = None) -> None:
    """Function to take a screenshot and save it."""
    img = pyautogui.screenshot()
    
    if save_path is None:
        # Use the default path if save_path is None
        save_path = r'C:\Users\vadla\OneDrive\Pictures\Screenshots\screenshot.png'
    else:
        # Ensure the directory exists
        directory = os.path.dirname(save_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
def keyEvent(key_code):
    # Simulate key event using adb shell
    command = f'adb shell input keyevent {key_code}'
    os.system(command)
    time.sleep(1)

def tapEvents(x, y):
    # Simulate tap event using adb shell
    command = f'adb shell input tap {x} {y}'
    os.system(command)
    time.sleep(1)

def adbInput(message):
    # Simulate input text event using adb shell
    # Escape special characters in the message
    escaped_message = message.replace(' ', '%s').replace(';', '\\;').replace('\'', '\\\'')
    command = f'adb shell input text "{escaped_message}"'
    os.system(command)
    time.sleep(1)

def goback(key_code):
    # Simulate multiple key events to go back
    for _ in range(6):
        keyEvent(key_code)

def replace_spaces_with_percent_s(input_string):
    # Replace spaces with '%s' in the input string
    return input_string.replace(' ', '%s')
