import sounddevice as sd
from scipy.io.wavfile import write
import os

class AudioRecorder:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def get_audio(self, filename, duration):
        try:
            # Ensure the directory for the filename exists
            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            print("Recording...")
            # Start recording
            recording = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=2, dtype='int16')
            sd.wait()  # Wait until the recording is finished
            
            # Write the recorded data to a WAV file
            write(filename, self.sample_rate, recording)
            
            # Confirm file creation
            if os.path.exists(filename):
                print(f"Recording finished. Saved as {filename}.")
            else:
                print("Recording failed: File was not created.")
        except Exception as e:
            print(f"Error during recording: {e}")

# Example usage
if __name__ == "__main__":
    recorder = AudioRecorder(sample_rate=44100)
    recorder.get_audio("output_test.wav", 5)  # Records a 5-second audio clip to output_test.wav
