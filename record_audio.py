import sounddevice as sd
from scipy.io.wavfile import write
import os
import numpy as np

class AudioRecorder:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.recording = []  # List to store audio chunks
        self.is_recording = False

    def start_recording(self):
        """Start recording audio continuously."""
        self.is_recording = True
        print("Recording started...")

        # Function to capture audio in chunks
        def callback(indata, frames, time, status):
            if status:
                print(status)
            if self.is_recording:
                self.recording.append(indata.copy())

        # Start streaming audio
        self.stream = sd.InputStream(samplerate=self.sample_rate, channels=2, callback=callback, dtype='int16')
        self.stream.start()

    def stop_recording(self, filename):
        """Stop recording and save the audio as a single file."""
        self.is_recording = False
        self.stream.stop()
        self.stream.close()

        # Combine all recorded chunks into a single array
        audio_data = np.concatenate(self.recording, axis=0)

        # Ensure the directory for the filename exists
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # Write the entire recording to a file
        write(filename, self.sample_rate, audio_data)
        print(f"Recording finished and saved as {filename}.")

# Example usage
if __name__ == "__main__":
    recorder = AudioRecorder(sample_rate=44100)
    recorder.start_recording()
    print("Recording for 5 seconds...")
    sd.sleep(5000)  # Record for 5 seconds as an example
    recorder.stop_recording("output_test.wav")
