import datetime
import pyttsx3
import speech_recognition as sr
import eel

# Initialize eel
eel.init('web')

# Global variable to store the schedule data
stored_schedule_keys = {}

def speak(message):
    try:
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in speak function: {e}")

@eel.expose
def scheduled(data):
    """
    Load the schedule data from the provided JSON and map days to their values.
    """
    global stored_schedule_keys
    stored_schedule_keys = {}
    schedules = data.get('Schedule', [])

    # Days of the week to map keys
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Iterate over schedules and map them to stored_schedule_keys
    for item in schedules:
        day_name = item.get('day')
        schedule_text = item.get('schedule')
        if day_name in weekdays:  # Check if the day_name matches a weekday
            stored_schedule_keys[day_name.lower()] = schedule_text

    # print("Schedule data stored:", stored_schedule_keys)

def schedule(day_name=None):
    """
    Retrieve the schedule for a specific day or today's schedule.
    """
    if not day_name:
        # Get today's weekday name
        day = datetime.datetime.today().strftime("%A").lower()
    else:
        day = day_name.lower()

    if day in stored_schedule_keys:
        message = stored_schedule_keys[day]
        eel.DisplayMessage(message)()  # Call the JavaScript function to display the message
        speak(message)
    else:
        speak(f"Boss, I don't have the schedule for {day.capitalize()}. Please check the day and try again.")

def command_handler(command):
    """
    Process user commands to handle schedules and exit requests.
    """
    print(f"Handling command: {command}")  # Debugging line
    command = command.lower()  # Convert command to lowercase
    if 'schedule on' in command:
        found_day = False
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            if day in command:
                print(f"Day found: {day}")  # Debugging line
                main(day)  # Pass the day to the main function
                found_day = True
                break
        if not found_day:
            speak("Sorry, I didn't catch which day you meant. Please specify a valid day of the week.")
    elif 'exit' in command:
        speak("Exiting. Have a nice day, Boss!")
        return True
    else:
        speak("Sorry, I didn't understand that command. Please say 'schedule on' followed by the day of the week, or 'exit' to stop.")

    return False

def takecommand():
    """
    Capture voice input from the user.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening...')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=15, phrase_time_limit=10)
            print('Recognizing...')
            query = r.recognize_google(audio)
            print(f"User said: {query}")
            return query.lower()
        except sr.RequestError as e:
            print(f"RequestError: {e}")
            speak("Sorry, I could not process your request. Please try again later.")
        except sr.UnknownValueError:
            print("UnknownValueError: Could not understand the audio.")
            speak("Sorry, I didn't understand the audio. Please speak clearly.")
        except Exception as e:
            print(f"Exception: {e}")
            speak("An unexpected error occurred. Please try again.")
    return ""

def main(day_name=None):
    """
    Main function to handle scheduling for a specific day or today.
    """
    if day_name:
        schedule(day_name)  # Pass the day_name to the schedule function
    else:
        schedule()  # Default schedule for today

if __name__ == "__main__":
    # Start the eel app

    while True:
        command = takecommand()  # Capture user command
        if command:  # Ensure command is not empty
            if command_handler(command):  # Break the loop if exit command is given
                break