import requests
import pyttsx3
import speech_recognition as sr
import webbrowser
from PIL import Image, ImageTk
from io import BytesIO
import tkinter as tk
import eel
import threading
eel.init('web')

def speak(text: str) -> None:
    """Function to speak out the given text."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen() -> str:
    """Function to listen to the user's speech and convert it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening")
        eel.DisplayMessage("Listening")
        audio = recognizer.listen(source)
    try:
        eel.DisplayMessage("Recognizing")
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"User said: {text}")
        eel.DisplayMessage(f"User said: {text}")
        return text.lower()
    except sr.UnknownValueError:
        speak("Sorry, I could not understand that.")
        return ""
    except sr.RequestError as e:
        speak(f"Could not request results from speech recognition service; {e}")
        return ""
@eel.expose
def DisplayMessage(message: str):
    """Display the message in a pop-up window using eel."""
    eel.DisplayMessage(message)

def get_weather_url(city: str, apiKey: str) -> str:
    """Generate the weather API URL."""
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    return f"{base_url}?q={city}&appid={apiKey}&units=metric"
stored_chatbot_keys = {}
def weather(data):
    global stored_chatbot_keys
    stored_chatbot_keys = {}
    chatbot_keys = data.get('ChatbotKeys', [])
    for key in chatbot_keys:
        if key.get('keyName') == 'weatherid':
            api_key = key.get('apiKey')
            if api_key:
                stored_chatbot_keys['weatherid'] = api_key
eel.expose(weather)

def fetch_weather(city: str) -> dict:
    """Fetch the weather data for the given city."""
    apiKey =stored_chatbot_keys.get('weatherid')
    url = get_weather_url(city, apiKey)
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        speak(f"Error fetching weather data: {e}")
        return None

def DisplayMessage(message: str):
    """Display the message in a pop-up window using eel."""
    eel.DisplayMessage(message)

def display_image_from_url(image_url: str) -> Image:
    """Fetch and return an image from a URL."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return img
    except requests.RequestException as e:
        speak(f"An error occurred while fetching the image: {str(e)}")
        return None

def display_weather_data(weather_dict: dict, city: str) -> None:
    """Display the weather data in the GUI."""
    if weather_dict.get('cod') == 200:
        main = weather_dict['main']
        weather_desc = weather_dict['weather'][0]
        icon_code = weather_desc['icon']
        description = weather_desc['main'].lower()

        # Define weather icons with Unicode symbols
        weather_icons = {
            "clear": "☀️",
            "rain": "🌧️",
            "clouds": "☁️",
            "snow": "❄️",
            "thunderstorm": "⛈️",
            "drizzle": "🌦️",
            "mist": "🌫️",
            "haze": "🌫️",
            "fog": "🌫️",
            "dust": "🌪️",
            "sand": "🌪️",
            "smoke": "🌫️",
            "tornado": "🌪️"
        }

        # Get the Unicode symbol for the weather description
        weather_icon = weather_icons.get(description, "🌡️")  # Default to a thermometer if no match

        # Update the GUI with weather information
        weather_label.config(text=f"Weather in {city}: {weather_icon} {weather_desc['main']} - {weather_desc['description']}")
        temp_label.config(text=f"🌡️ Temperature: {main['temp']}°C")
        humidity_label.config(text=f"💧 Humidity: {main['humidity']}%")

        # Display the weather icon
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        img = display_image_from_url(icon_url)
        if img:
            img = img.resize((100, 100))  # Resize image to fit GUI
            img_tk = ImageTk.PhotoImage(img)
            icon_label.config(image=img_tk)
            icon_label.image = img_tk  # Keep a reference to avoid garbage collection

        # Optionally, speak out the weather data
        speak(f"Weather in {city}: {weather_desc['main']}, {weather_desc['description']}, Temperature: {main['temp']}°C, Humidity: {main['humidity']}%")

        # Show the message in the pop-up
        DisplayMessage(f"Weather in {city}: {weather_icon} {weather_desc['main']}, Temp: {main['temp']}°C")
    else:
        weather_label.config(text=f"Error fetching weather data. Code: {weather_dict.get('cod')}")
        speak(f"Error fetching weather data. Code: {weather_dict.get('cod')}")
        DisplayMessage(f"Error fetching weather data. Code: {weather_dict.get('cod')}")

def update_weather() -> None:
    """Update the weather data based on the entered city."""
    city = city_entry.get()
    weather_dict = fetch_weather(city)
    if weather_dict:
        display_weather_data(weather_dict, city)

def get_location() -> str:
    """Get the city name based on the user's IP address."""
    try:
        response = requests.get('https://ipinfo.io')
        location_data = response.json()
        city = location_data.get('city', '')
        return city
    except requests.RequestException as e:
        speak(f"An error occurred while retrieving location data: {str(e)}")
        return ""

def ask_for_location() -> str:
    """Ask the user to speak their city name."""
    speak("Please say the name of your city.")
    city = listen()
    if not city:
        speak("Sorry, I didn't catch that. Please try again.")
        city = listen()
    return city

def ask_location_preference() -> str:
    """Ask the user if they want to use their current location or specify a location."""
    eel.DisplayMessage("Would you like to use your current location or specify a location? Say 'my location' for your current location or 'specify' to enter a city name.")
    speak("Would you like to use your current location or specify a location? Say 'current' for your current location or 'specify' to enter a city name.")
    preference = listen()
    if preference == 'my location':
        return get_location()
    elif preference == 'specify':
        speak("Please say the name of your city.")
        return listen()
    else:
        speak("Sorry, I didn't understand that. Please try again.")
        return ask_location_preference()


# Other imports and function definitions remain the same

def continuous_listen():
    """Continuously listen for voice commands and handle them."""
    while True:
        command = listen()
        if command:
            if 'weather' in command:
                city = city_entry.get()
                if not city:
                    city = ask_location_preference()
                    if city:
                        city_entry.insert(0, city)
                update_weather()
            elif 'exit' in command or 'quit' in command:
                speak("Exiting the application.")
                root.destroy()
                break
            else:
                speak("Sorry, I didn't understand that command.")

def main():
    global weather_label, temp_label, humidity_label, icon_label, city_entry, root

    # Tkinter GUI setup
    root = tk.Tk()
    root.title("Weather Application")
    root.configure(bg='orange')  # Set background color to orange

    # Layout the GUI
    city_label = tk.Label(root, text="Enter City:", bg='orange')
    city_label.grid(row=0, column=0)

    city_entry = tk.Entry(root)
    city_entry.grid(row=0, column=1)

    weather_button = tk.Button(root, text="Get Weather", command=update_weather)
    weather_button.grid(row=0, column=2)

    # Weather Info Display with Unicode icons
    weather_label = tk.Label(root, text="Weather: ", font=('bold', 14), bg='orange')
    weather_label.grid(row=1, column=1)

    temp_label = tk.Label(root, text="Temperature: ", font=('bold', 14), bg='orange')
    temp_label.grid(row=2, column=1)

    humidity_label = tk.Label(root, text="Humidity: ", font=('bold', 14), bg='orange')
    humidity_label.grid(row=3, column=1)

    icon_label = tk.Label(root)
    icon_label.grid(row=1, column=2, rowspan=3)

    # Ask for location preference and update weather
    city = ask_location_preference()
    if city:
        speak(f"Getting the weather report for {city}.")
        city_entry.insert(0, city)  # Pre-fill the city entry field
        update_weather()

    # Start the continuous listening thread
    listening_thread = threading.Thread(target=continuous_listen, daemon=True)
    listening_thread.start()

    # Run the application
    root.mainloop()


if __name__ == '__main__':
    main()
