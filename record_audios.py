import os
import numpy as np
import soundcard as sc
import soundfile as sf
import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SystemAudioRecorder:
    def __init__(self, sample_rate=44100, channels=2):
        """
        Initialize the system audio recorder.
        
        :param sample_rate: Audio sampling rate (default 44100 Hz)
        :param channels: Number of audio channels (default 2 for stereo)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.recording_thread = None
        self.audio_data = []
        self.output_device = None
        
        try:
            self.output_device = sc.default_speaker()
            logging.info(f"Selected audio output device: {self.output_device.name}")
        except Exception as e:
            logging.error(f"Error selecting audio device: {e}")
            raise

    def _record_audio(self):
        """Internal method to record audio in a thread."""
        logging.info("Recording started...")
        try:
            with self.output_device.recorder(samplerate=self.sample_rate, channels=self.channels) as recorder:
                while self.is_recording:
                    data = recorder.record(numframes=1024)
                    self.audio_data.append(data)
        except Exception as e:
            logging.error(f"Error during audio recording: {e}")

    def start_recording(self):
        """Start recording system audio."""
        if self.is_recording:
            logging.warning("Recording is already in progress.")
            return
        
        self.is_recording = True
        self.audio_data = []
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.start()
        logging.info("System audio recording started.")

    def stop_recording(self, filename):
        """
        Stop recording and save the audio file.
        
        :param filename: Path to save the audio file
        """
        if not self.is_recording:
            logging.warning("No active recording to stop.")
            return False

        self.is_recording = False
        self.recording_thread.join()  # Wait for the recording thread to finish

        # Concatenate all recorded audio chunks
        if self.audio_data:
            audio_data = np.concatenate(self.audio_data, axis=0)

            # Normalize audio to prevent clipping
            audio_data = audio_data / np.max(np.abs(audio_data))

            # Save the audio file
            try:
                sf.write(filename, audio_data, self.sample_rate, subtype='PCM_16')
                logging.info(f"Recording saved successfully: {filename}")
                return True
            except Exception as e:
                logging.error(f"Error saving audio file: {e}")
                return False
        else:
            logging.warning("No audio data recorded.")
            return False
