# Google Meet Bot

This project is a Python bot that automates the process of logging into Gmail, joining a Google Meet, turning off the microphone and camera, recording the meeting, extracting audio, and transcribing the conversation using Whisper and FFmpeg.

## Features
- Automatically logs into Google using the provided credentials.
- Joins a specified Google Meet link.
- Turns off the microphone and camera before joining.
- Enters a name ("Bot") if required and clicks "Ask to Join".
- Records the entire meeting using FFmpeg.
- Extracts audio from the recorded video.
- Transcribes the audio into text using Whisper.
- Handles dynamic elements and waits for page load.

## Prerequisites
- Python 3.8 or higher
- Google Chrome browser
- ChromeDriver (compatible with the installed Chrome version)
- FFmpeg (for recording and extracting audio)
- OpenAI Whisper model for transcription
- A Gmail account
- A Google Meet link

## Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/hritick99/google_meet_bot.git
cd google-meet-bot
```

### 2️⃣ Set Up a Virtual Environment
```bash
python -m venv env
```

### 3️⃣ Activate the Virtual Environment
- **Windows:**
  ```bash
  env\Scripts\activate
  ```
- **Mac/Linux:**
  ```bash
  source env/bin/activate
  ```

### 4️⃣ Install Required Dependencies
```bash
pip install -r requirements.txt
```

### 5️⃣ Install ChromeDriver
Ensure that ChromeDriver is installed and matches your Google Chrome version.
- **Windows:** Download from [ChromeDriver](https://chromedriver.chromium.org/downloads) and place it in the project folder.
- **Linux/Mac:** Install using:
  ```bash
  sudo apt install chromedriver  # Linux
  brew install chromedriver      # Mac
  ```

### 6️⃣ Install FFmpeg
FFmpeg is required for recording and extracting audio.
- **Windows:** Download from [FFmpeg](https://ffmpeg.org/download.html), extract it, and add it to your system path.
- **Linux:**
  ```bash
  sudo apt install ffmpeg
  ```
- **Mac:**
  ```bash
  brew install ffmpeg
  ```

## Usage

### Running the Bot
```bash
python join_google_meet.py
```

When prompted, enter your Gmail credentials. The bot will then:
1. Log into Google.
2. Navigate to the specified Google Meet link.
3. Turn off the microphone and camera.
4. Enter "Bot" as the name if required.
5. Click "Ask to Join" if necessary.
6. Start recording the meeting using FFmpeg.
7. Extract audio from the recorded video.
8. Transcribe the audio into text using Whisper.

## Recording and Transcription Process
1. **Recording:**
   - The bot uses FFmpeg to record both video and audio of the meeting.
   - The recorded file is saved as an MP4.
2. **Extracting Audio:**
   - After the meeting, FFmpeg extracts the audio from the MP4 file.
   - The extracted audio is saved as a WAV file.
3. **Transcribing Audio:**
   - Whisper transcribes the audio and generates a text file with the conversation.

## Troubleshooting

### 1️⃣ ChromeDriver Version Issue
If you see an error related to ChromeDriver, ensure that:
- Your ChromeDriver version matches your Chrome browser version.
- You have added ChromeDriver to your system `PATH`.

### 2️⃣ Google Account Security Block
If Google prevents the login, try:
- Enabling "Less Secure Apps" in your Google Account settings.
- Using an app-specific password.

### 3️⃣ FFmpeg Not Found
- Ensure FFmpeg is installed and added to the system path.
- Run `ffmpeg -version` to verify installation.

### 4️⃣ Elements Not Found Error
If an element is not found:
- Increase the explicit wait time in the script.
- Ensure the Google Meet interface has not changed.

## Contributing
Feel free to fork this repository and submit pull requests for enhancements or bug fixes.

## License
This project is licensed under the MIT License.

