import os
import time
import whisper
import warnings
import logging
import subprocess
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress warnings globally
warnings.filterwarnings("ignore")


class JoinGoogleMeet:
    def __init__(self, email=None, password=None):
        self.mail_address = email or input("Enter your Gmail address: ")
        self.password = password or input("Enter your Gmail password: ")

        # Chrome setup
        opt = Options()
        opt.add_argument('--disable-blink-features=AutomationControlled')
        opt.add_argument('--start-maximized')
        opt.add_argument("--log-level=3")  # Suppress unnecessary logs
        opt.add_experimental_option("excludeSwitches", ["enable-logging"])
        opt.add_experimental_option("prefs", {
            "profile.default_content_setting_values.media_stream_mic": 1,
            "profile.default_content_setting_values.media_stream_camera": 1,
            "profile.default_content_setting_values.geolocation": 0,
            "profile.default_content_setting_values.notifications": 1
        })
        try:
            self.driver = webdriver.Chrome(options=opt)
        except Exception as e:
            logging.error(f"Error initializing Chrome WebDriver: {e}")
            raise

    def Glogin(self):
        """Login to Google Account."""
        self.driver.get(
            'https://accounts.google.com/ServiceLogin?hl=en&passive=true&continue=https://www.google.com/&ec=GAZAAQ')
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            ).send_keys(self.mail_address)
            self.driver.find_element(By.ID, "identifierNext").click()
            self.driver.implicitly_wait(10)

            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input'))
            ).send_keys(self.password)
            self.driver.find_element(By.ID, "passwordNext").click()
            self.driver.implicitly_wait(10)

            self.driver.get('https://google.com/')
            self.driver.implicitly_wait(10)
            logging.info("Gmail login activity: Done")
        except Exception as e:
            logging.error(f"Error during Gmail login: {e}")

    def turnOffMicCam(self, meet_link):
        """Turn off microphone and camera."""
        self.driver.get(meet_link)
        time.sleep(3)

        try:
            # Turn off Camera
            camera_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="button"][aria-label*="camera"]'))
            )
            camera_button.click()
            logging.info("Camera turned off.")
        except TimeoutException:
            logging.warning("Camera button not found or failed to click.")

        try:
            # Turn off Mic
            mic_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="button"][aria-label*="microphone"]'))
            )
            mic_button.click()
            logging.info("Microphone turned off.")
        except TimeoutException:
            logging.warning("Microphone button not found or failed to click.")

    def enter_bot_name(self):
        """If prompted, enter 'Bot' as the name and proceed to ask to join."""
        try:
            name_input = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "c6"))
            )
            name_input.clear()
            name_input.send_keys("Bot")
            logging.info("Entered name as 'Bot'")
        except TimeoutException:
            logging.info("No name prompt found. Skipping name entry.")

    def ask_to_join(self):
        """Click on 'Ask to Join' if not automatically admitted."""
        try:
            self.enter_bot_name()
            ask_to_join_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[jsname="V67aGc"]'))
            )
            ask_to_join_button.click()
            logging.info("Clicked on 'Ask to Join' button.")
        except TimeoutException:
            logging.warning("Ask to Join button not found. Admission may be required.")

    def wait_and_monitor_participants(self):
        """
        Continuously monitor participant count during the meeting.
        If the count drops below 2, stop recording by sending 'q' to FFmpeg
        and then leave the meeting.
        """
        logging.info("Starting participant monitoring...")
        while True:
            try:
                participant_count_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.gFyGKf.BN1Lfc div.uGOf1d'))
                )
                num_participants = int(participant_count_element.text.strip())
                logging.info(f"Current number of participants: {num_participants}")

                if num_participants < 2:
                    logging.warning("Participant count dropped below 2. Stopping recording and leaving the meeting.")
                    # Send 'q' to the FFmpeg process to stop recording
                    if hasattr(self, 'recording_process') and self.recording_process:
                        self.recording_process.communicate(input=b'q\n')
                    self.leave_meeting()
                    return

            except (TimeoutException, NoSuchElementException, ValueError):
                logging.warning("Unable to retrieve participant count. Retrying...")
            time.sleep(3)  # Check participant count every 3 seconds

    # def stop_recording(self):
    #     """Stops the ongoing recording process."""
    #     try:
    #         logging.info("Stopping the recording process.")
    #         # Send a termination signal to FFmpeg process
    #         if hasattr(self, 'recording_process') and self.recording_process:
    #             self.recording_process.terminate()
    #             self.recording_process.wait()
    #             logging.info("Recording stopped successfully.")
    #     except Exception as e:
    #         logging.error(f"Error while stopping recording: {e}")

    def record_desktop(self, video_file):
        """
        Runs the FFmpeg command to record desktop video and audio.
        
        Args:
            video_file (str): Path to save the recorded MP4 file.
        """
        try:
            # FFmpeg command for recording
            ffmpeg_command = [
                "ffmpeg",
                "-f", "gdigrab",
                "-framerate", "30",
                "-i", "desktop",
                "-f", "dshow",
                "-i", "audio=Stereo Mix (Realtek(R) Audio)",
                "-c:v", "libx264",
                "-profile:v", "baseline",
                "-pix_fmt", "yuv420p",
                "-preset", "ultrafast",
                "-c:a", "libmp3lame",
                "-b:a", "192k",
                "-movflags", "+faststart",
                "-y",
                video_file
            ]

            logging.info(f"Starting FFmpeg recording. Output file: {video_file}")
            self.recording_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)

            # Wait for the process to complete or stop with 'q'
            while self.recording_process.poll() is None:
                time.sleep(1)

            logging.info("Recording process has stopped.")
        except Exception as e:
            logging.error(f"Error during recording: {e}")


    def leave_meeting(self):
        """Leave the meeting."""
        try:
            leave_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Leave call"]')
            leave_button.click()
            logging.info("Left the meeting.")
        except NoSuchElementException:
            logging.warning("Leave button not found.")
            
    def extract_audio(self,video_file, audio_file):
        """
        Extracts audio from a video file and saves it as a WAV file.
        
        Args:
            video_file (str): Path to the input video file.
            audio_file (str): Path to save the extracted audio file.
        """
        try:
            # FFmpeg command to extract audio
            ffmpeg_command = [
                "ffmpeg",
                "-i", video_file,
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", "44100",
                "-ac", "2",
                "-y",
                audio_file
            ]

            logging.info(f"Extracting audio from {video_file} to {audio_file}")
            subprocess.run(ffmpeg_command, check=True)
            logging.info(f"Audio extracted successfully: {audio_file}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error during audio extraction: {e}")



    def transcribe_audio(self,audio_file, transcription_file):
        """
        Transcribes audio to text using Whisper and saves the transcription.
        
        Args:
            audio_file (str): Path to the audio file.
            transcription_file (str): Path to save the transcription text file.
        """
        try:
            logging.info("Loading Whisper model...")
            model = whisper.load_model("medium")  # Available models: tiny, base, small, medium, large

            logging.info(f"Transcribing audio from {audio_file}")
            result = model.transcribe(audio_file)
            transcription = result["text"]

            # Save transcription to a text file
            with open(transcription_file, "w", encoding="utf-8") as f:
                f.write(transcription)
            logging.info(f"Transcription saved to: {transcription_file}")
        except Exception as e:
            logging.error(f"Error during transcription: {e}")



def main():
    try:
        output_dir = "recordings"
        os.makedirs(output_dir, exist_ok=True)

        obj = JoinGoogleMeet()
        obj.Glogin()
        obj.turnOffMicCam("https://meet.google.com/wqa-zksy-xxk")
        obj.ask_to_join()
        

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        video_path = os.path.join(output_dir, f"meeting_recording_{timestamp}.mp4")
        audio_path = os.path.join(output_dir, f"meeting_audio_{timestamp}.wav")
        transcription_path = os.path.join(output_dir, f"meeting_transcription_{timestamp}.txt")

        # Start monitoring participants in a separate thread
        monitor_thread = threading.Thread(target=obj.wait_and_monitor_participants, daemon=True)
        monitor_thread.start()
        
        obj.record_desktop(video_path)
        
        # Extract audio from the recorded video
        obj.extract_audio(video_path, audio_path)

        # Transcribe the extracted audio
        obj.transcribe_audio(audio_path, transcription_path)
        
    except Exception as e:
        logging.error(f"Error in the meeting process: {e}")


if __name__ == "__main__":
    main()
