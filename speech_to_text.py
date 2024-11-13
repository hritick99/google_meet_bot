import os
import subprocess
import datetime
import json
from openai import OpenAI, OpenAIError

class SpeechToText:
    def __init__(self, output_dir="output_files"):
        # Load API key from environment variable
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=api_key)
        self.MAX_AUDIO_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB max audio size
        self.output_dir = output_dir
        
        # Ensure the output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def get_file_size(self, file_path):
        return os.path.getsize(file_path)

    def get_audio_duration(self, audio_file_path):
        try:
            result = subprocess.run(
                ['ffprobe', '-i', audio_file_path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0'],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            return float(result.stdout)
        except Exception as e:
            print(f"Error getting audio duration: {e}")
            return None

    def resize_audio_if_needed(self, audio_file_path):
        audio_size = self.get_file_size(audio_file_path)
        if audio_size > self.MAX_AUDIO_SIZE_BYTES:
            current_duration = self.get_audio_duration(audio_file_path)
            if current_duration is None:
                return audio_file_path  # If duration check fails, skip resizing

            target_duration = current_duration * self.MAX_AUDIO_SIZE_BYTES / audio_size
            compressed_audio_path = os.path.join(
                self.output_dir, f'compressed_audio_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.wav'
            )

            print(f"Resizing audio to target duration {target_duration}s")
            result = subprocess.run(
                ['ffmpeg', '-i', audio_file_path, '-ss', '0', '-t', str(target_duration), compressed_audio_path]
            )
            if result.returncode == 0:
                print(f"Audio resized and saved to {compressed_audio_path}")
                return compressed_audio_path
            else:
                print("Audio resizing failed.")
        return audio_file_path

    def transcribe_audio(self, audio_file_path):
        try:
            with open(audio_file_path, 'rb') as audio_file:
                transcript = self.client.audio.translations.create(
                    file=audio_file,
                    model="whisper-1",
                )
            print("Transcription complete.")
            return transcript.text
        except OpenAIError as e:
            print(f"Error during transcription: {e}")
            return None

    def abstract_summary_extraction(self, transcription):
        return self._chat_request(
            transcription,
            "Summarize the following text into a concise abstract paragraph."
        )

    def key_points_extraction(self, transcription):
        return self._chat_request(
            transcription,
            "Identify and list the main points discussed in the following text."
        )

    def action_item_extraction(self, transcription):
        return self._chat_request(
            transcription,
            "List any action items discussed in the following text."
        )

    def sentiment_analysis(self, transcription):
        return self._chat_request(
            transcription,
            "Analyze the sentiment of the following text."
        )

    def _chat_request(self, transcription, prompt):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                temperature=0,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": transcription}
                ]
            )
            print(f"{prompt} - Completed")
            return response.choices[0].message.content
        except OpenAIError as e:
            print(f"Error during chat request: {e}")
            return None

    def meeting_minutes(self, transcription):
        return {
            'abstract_summary': self.abstract_summary_extraction(transcription),
            'key_points': self.key_points_extraction(transcription),
            'action_items': self.action_item_extraction(transcription),
            'sentiment': self.sentiment_analysis(transcription)
        }

    def store_in_json_file(self, data):
        # Save JSON file in the same directory as the output audio
        file_path = os.path.join(self.output_dir, f'meeting_data_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.json')
        print(f"Storing JSON file at: {file_path}")
        with open(file_path, 'w') as f:
            json.dump(data, f)
        print("JSON file created successfully.")

    def transcribe(self, audio_file_path):
        # Resize if needed and transcribe
        audio_file_path = self.resize_audio_if_needed(audio_file_path)
        transcription = self.transcribe_audio(audio_file_path)
        
        if transcription:
            # Generate meeting minutes and save them in JSON format
            summary = self.meeting_minutes(transcription)
            self.store_in_json_file(summary)

            # Display summaries
            print(f"Abstract Summary: {summary['abstract_summary']}")
            print(f"Key Points: {summary['key_points']}")
            print(f"Action Items: {summary['action_items']}")
            print(f"Sentiment: {summary['sentiment']}")
        else:
            print("Transcription failed. Meeting minutes not generated.")
