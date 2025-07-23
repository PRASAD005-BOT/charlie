
# Charlie - Voice Assistant

Charlie is a sophisticated voice assistant application built with Python that combines various features including voice recognition, web automation, system control, and integration with multiple services.

## Features

- 🎙️ Voice Recognition and Command Processing
- 🌐 Web Browser Integration
- 🎵 Music Control (Spotify Integration)
- 🗣️ Text-to-Speech Capabilities
- 🌍 Google Maps Integration
- 🌤️ Weather Information
- 📅 Schedule Management
- 📊 PowerPoint Integration
- 🚇 Subway Information
- 👤 Face Recognition
- 🔊 Multi-language Support
- 🤖 AI Chat Integration (HugChat)

## Tech Stack

- Python 3.x
- Eel (Web GUI Framework)
- Speech Recognition
- VLC Media Player
- Google Translate
- Spotify API
- PyAutoGUI
- Google Generative AI
- HugChat
- Various Python Libraries (check requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/PRASAD005-BOT/charlie.git
cd charlie
```

2. Create and activate a virtual environment:
```bash
python -m venv envcharlie
source envcharlie/Scripts/activate  # On Windows
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python main.py
```

2. The application will launch with a web interface and start listening for voice commands.

3. Use the wake word to activate the assistant and give commands.

## Available Commands

Here are some of the key commands you can use with Charlie:

### Communication
- "Call [contact name]" - Make a phone call to a saved contact
- "Send message to [contact name]" - Send a WhatsApp message to a contact
- "Video call [contact name]" - Start a WhatsApp video call

### Media Controls
- "Play [song/video name] on YouTube" - Plays videos on YouTube
- "Play [song name] on Spotify" - Controls Spotify playback
- "Stop song" - Stops current music playback
- "Play Instagram reels" - Opens Instagram reels

### Web Navigation
- "Open [website name]" - Opens saved websites in the browser
- You can configure custom website shortcuts in the settings

### System Controls
- "Open [application name]" - Opens installed applications
- Supports custom system paths configured in settings

### AI Chat
- Ask any question to get AI-powered responses using Gemini AI
- Support for natural language conversations

### Additional Features
- Weather information queries
- Schedule management
- PowerPoint control
- Subway information
- Face recognition commands
- Multi-language support for interactions

Note: Some features require additional configuration or API keys to work properly.

## Project Structure

- `main.py` - Main application entry point
- `engine/` - Core functionality modules
  - `features.py` - Main features implementation
  - `command.py` - Voice command processing
  - `spotify.py` - Spotify integration
  - `weather.py` - Weather information
  - `schedule_module.py` - Schedule management
  - And more...
- `www/` - Web interface files
  - `index.html` - Main interface
  - `style.css` - Styling
  - `script.js` - Frontend functionality

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Created by PRASAD005-BOT

## Acknowledgments

- Thanks to all the open-source libraries and APIs that made this project possible
- Special thanks to the Python community for the extensive documentation and support
=======


