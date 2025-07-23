import os
import subprocess
import eel
import threading
import webbrowser
from engine.features import *
from engine.spotify import *
from engine.command import *
from engine.schedule_module import *
from threading import Event
from playsound import playsound  # Ensure this import if using playsound

# Initialize Eel
eel.init("www")

# Create an event to signal the closure of the Eel app
stop_event = Event()
chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"  # Update this path if needed
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))

# Function to play the assistant sound
def playAssistantSound():
    sound_path = resource_path("www/assets/audio/start_sound.mp3")
    if os.path.isfile(sound_path):
        playsound(sound_path)
    else:
        print(f"Error: The sound file {sound_path} does not exist.")

# Function to start Jarvis
def startCharlie():
    print("Process 1 is running.")
    from main import start
    start()

# Function to run hotword detection
def listenHotword():
    print("Process 2 is running.")
    from engine.features import hotword
    hotword()

# Ensure the path to device.bat is correct
device_bat_path = r'C:\pytho\jarvis\device.bat'

def run_device_bat():
    if os.path.isfile(device_bat_path):
        try:
            # Run the batch file
            process = subprocess.Popen([device_bat_path], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()  # Capture output and errors
            if process.returncode == 0:
                print("device.bat has been started successfully.")
                print(f"Output: {stdout.decode()}")
            else:
                print(f"Error: device.bat returned a non-zero exit code {process.returncode}.")
                print(f"Error Output: {stderr.decode()}")
        except Exception as e:
            print(f"Failed to start device.bat: {e}")
    else:
        print(f"Error: The file {device_bat_path} does not exist.")

# Function to start Eel in a non-blocking way
def start_eel():
    eel.start('index.html', size=(1060, 600), mode='chrome')
    print("Eel has started.")

# Function to run the tasks in a single thread
def main():
    print("Running device.bat.")
    run_device_bat()

    # Proceed with starting Jarvis and hotword detection
    print("Starting Jarvis and hotword detection.")
    startCharlie()
    listenHotword()

    # Start Eel
    print("Starting Eel.")
    start_eel()

    # Event loop to keep the application running
    try:
        while not stop_event.is_set():
            stop_event.wait(timeout=1)  # Check if stop_event is set
    except KeyboardInterrupt:
        print("Interrupted by user.")

    print("System stop")
# Run continuous listening in a separate th

if __name__ == '__main__':
    main()