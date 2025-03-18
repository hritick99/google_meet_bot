import subprocess
import logging
import os
import whisper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def record_desktop(video_file):
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
        process = subprocess.Popen(ffmpeg_command)

        # Wait for the process to complete or terminate manually
        try:
            process.wait()
        except KeyboardInterrupt:
            logging.info("Recording interrupted by user. Finalizing the file...")
            process.terminate()
            process.wait()

    except Exception as e:
        logging.error(f"Error during recording: {e}")

def extract_audio(video_file, audio_file):
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

def transcribe_audio(audio_file, transcription_file):
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

if __name__ == "__main__":
    # Ensure output directory exists
    output_dir = "recordings"
    os.makedirs(output_dir, exist_ok=True)

    # File paths
    video_file = os.path.join(output_dir, "test_recording.mp4")
    audio_file = os.path.join(output_dir, "output_audio.wav")
    transcription_file = os.path.join(output_dir, "transcription.txt")

    # Step 1: Record the desktop
    logging.info("Starting desktop recording...")
    record_desktop(video_file)

    # Step 2: Extract audio from the recorded video
    if os.path.exists(video_file):
        logging.info("Extracting audio from the recorded video...")
        extract_audio(video_file, audio_file)

        # Step 3: Transcribe the extracted audio to text
        if os.path.exists(audio_file):
            logging.info("Transcribing audio to text...")
            transcribe_audio(audio_file, transcription_file)
        else:
            logging.error("Audio extraction failed. No audio file found.")
    else:
        logging.error("Recording failed. No video file found.")
