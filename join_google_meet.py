import os
import time
import whisper
import warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from record_audio import AudioRecorder

# Suppress warnings globally
warnings.filterwarnings("ignore")

class JoinGoogleMeet:
    def __init__(self, email=None, password=None):
        # Allow email and password to be provided as arguments or prompt for them if not provided
        self.mail_address = email or input("Enter your Gmail address: ")
        self.password = password or input("Enter your Gmail password: ")

        # create chrome instance with suppressed logging
        opt = Options()
        opt.add_argument('--disable-blink-features=AutomationControlled')
        opt.add_argument('--start-maximized')
        opt.add_argument("--log-level=3")  # Minimize logging to suppress errors and warnings
        opt.add_experimental_option("excludeSwitches", ["enable-logging"])  # Suppress unnecessary logs
        opt.add_experimental_option("prefs", {
            "profile.default_content_setting_values.media_stream_mic": 1,
            "profile.default_content_setting_values.media_stream_camera": 1,
            "profile.default_content_setting_values.geolocation": 0,
            "profile.default_content_setting_values.notifications": 1
        })
        self.driver = webdriver.Chrome(options=opt)

    def Glogin(self):
        # Login Page
        self.driver.get(
            'https://accounts.google.com/ServiceLogin?hl=en&passive=true&continue=https://www.google.com/&ec=GAZAAQ')

        # input Gmail
        self.driver.find_element(By.ID, "identifierId").send_keys(self.mail_address)
        self.driver.find_element(By.ID, "identifierNext").click()
        self.driver.implicitly_wait(10)

        # input Password
        self.driver.find_element(By.XPATH,
            '//*[@id="password"]/div[1]/div/div[1]/input').send_keys(self.password)
        self.driver.implicitly_wait(10)
        self.driver.find_element(By.ID, "passwordNext").click()
        self.driver.implicitly_wait(10)    
        # go to google home page
        self.driver.get('https://google.com/')
        self.driver.implicitly_wait(10)
        print("Gmail login activity: Done")

    def turnOffMicCam(self, meet_link):
        # Navigate to Google Meet URL
        self.driver.get(meet_link)
        time.sleep(3)  # Allow time for page to load

        # Turn off Microphone
        try:
            mic_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="button"][aria-label="Turn off microphone"]'))
            )
            mic_button.click()
            print("Microphone turned off.")
        except TimeoutException:
            print("Mic button not found or failed to click.")

        # Turn off Camera
        try:
            camera_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="button"][aria-label="Turn off camera"]'))
            )
            camera_button.click()
            print("Camera turned off.")
        except TimeoutException:
            print("Camera button not found or failed to click.")

    def ask_to_join(self):
        """Click on 'Ask to Join' if not automatically admitted."""
        try:
            ask_to_join_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[jsname="Qx7uuf"]'))
            )
            ask_to_join_button.click()
            print("Clicked on 'Ask to Join' button.")

            # Wait until joined or admitted
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[jscontroller="CkHiJd"]'))
            )
            print("Successfully joined the meeting.")
        except TimeoutException:
            print("Failed to join the meeting. Waiting for admission may be required.")
        except NoSuchElementException:
            print("Ask to Join button not found.")

    def check_participants(self):
        """Check the number of participants in the meeting."""
        try:
            participant_count_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.gFyGKf.BN1Lfc .uGOf1d'))
            )
            num_participants = int(participant_count_element.text)
            print(f"Number of participants: {num_participants}")
            return num_participants
        except (TimeoutException, NoSuchElementException, ValueError):
            print("Could not retrieve participant count.")
            return 1  # Default to 1 if participant count cannot be determined

    def leave_meeting(self):
        """Leave the meeting if only one participant (the bot) remains."""
        try:
            leave_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Leave call"]')
            leave_button.click()
            print("Left the meeting as only one participant remains.")
        except NoSuchElementException:
            print("Leave button not found.")

    def record_meeting(self, audio_recorder, audio_path):
        """Start and stop recording based on meeting status."""
        audio_recorder.start_recording()

        while True:
            # Check if there are participants
            num_participants = self.check_participants()
            if num_participants <= 1:  # Stop recording if only the bot is in the meeting
                audio_recorder.stop_recording(audio_path)
                self.leave_meeting()
                break

            time.sleep(1)  # Check every second

    def transcribe_audio(self, audio_path):
        """Use Whisper for high-quality transcription."""
        print("Transcribing audio...")
        model = whisper.load_model("base")  # Use a higher model for better accuracy, e.g., "medium" or "large"
        result = model.transcribe(audio_path)
        transcription = result['text']
        print("Transcription complete.")
        
        # Save transcription to a file
        transcript_path = os.path.splitext(audio_path)[0] + "_transcription.txt"
        with open(transcript_path, "w") as f:
            f.write(transcription)
        print(f"Transcription saved to {transcript_path}")

def main():
    # Initialize Google Meet bot with email and password prompt
    obj = JoinGoogleMeet()
    obj.Glogin()
    obj.turnOffMicCam("https://meet.google.com/via-dfob-tud")
    
    # Ask to join the meeting if required
    obj.ask_to_join()

    # Record the entire meeting as a single audio file
    audio_recorder = AudioRecorder(sample_rate=44100)
    audio_path = "meeting_recording.wav"
    obj.record_meeting(audio_recorder, audio_path)

    # Transcribe the complete audio file using Whisper
    obj.transcribe_audio(audio_path)

# Run the main function
if __name__ == "__main__":
    main()
