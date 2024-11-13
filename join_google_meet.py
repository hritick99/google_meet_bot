# import required modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
import tempfile
from record_audio import AudioRecorder
from speech_to_text import SpeechToText

class JoinGoogleMeet:
    def __init__(self):
        self.mail_address = os.environ.get('email_id')
        self.password = os.environ.get('email_password')
        # create chrome instance
        opt = Options()
        opt.add_argument('--disable-blink-features=AutomationControlled')
        opt.add_argument('--start-maximized')
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
        self.driver.implicitly_wait(100)
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

    def checkIfJoined(self):
        try:
            # Wait for the join button to appear
            join_button = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.uArJ5e.UQuaGc.Y5sE8d.uyXBBb.xKiqt'))
            )
            print("Meeting has been joined")
        except (TimeoutException, NoSuchElementException):
            print("Meeting has not been joined")

    def AskToJoin(self, audio_path, duration):
        # Ask to Join meet
        try:
            ask_to_join_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[jsname="Qx7uuf"]'))
            )
            ask_to_join_button.click()
            print("Clicked on 'Ask to Join'")
        except TimeoutException:
            print("Ask to Join button not found.")

        # Record audio
        AudioRecorder().get_audio(audio_path, duration)
        print("Audio recording completed.")

def main():
    # Set a unified output directory
    output_dir = "output_files"
    os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists
    audio_path = os.path.join(output_dir, "output.wav")  # Audio file path in output_dir

    # Meeting link and audio duration for recording
    meet_link = 'https://meet.google.com/via-dfob-tud'
    duration = 60

    # Initialize Google Meet bot
    obj = JoinGoogleMeet()
    obj.Glogin()
    obj.turnOffMicCam(meet_link)
    obj.AskToJoin(audio_path, duration)  # Record audio and join the meeting

    # Transcription and summary generation after meeting ends
    speech_to_text = SpeechToText(output_dir=output_dir)
    speech_to_text.transcribe(audio_path)  # Generate transcription and save JSON in output_dir

# Run the main function
if __name__ == "__main__":
    main()
