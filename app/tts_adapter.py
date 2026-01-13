"""
tts_adapter.py

Amazon Polly TTS adapter. Writes MP3 files to output/ and returns the path.

Note:
- Expects AWS credentials and region to be provided via environment variables:
  AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
"""
import os
from typing import Optional
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from utils import get_env


def text_to_speech(text: str, output_file: str = "output.mp3", voice: str = "Matthew") -> Optional[str]:
    """
    Convert text to speech using Amazon Polly.

    Returns:
        Path to saved mp3 file, or None when failed.
    """
    aws_key = get_env("AWS_ACCESS_KEY_ID")
    aws_secret = get_env("AWS_SECRET_ACCESS_KEY")
    aws_region = get_env("AWS_REGION")

    if not (aws_key and aws_secret and aws_region):
        # AWS not configured; cannot produce TTS
        return None

    polly = boto3.client(
        "polly",
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret,
        region_name=aws_region
    )

    try:
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId=voice
        )
        audio_stream = response.get("AudioStream")
        if audio_stream is None:
            return None

        os.makedirs("output", exist_ok=True)
        file_path = os.path.join("output", output_file)

        # audio_stream is a StreamingBody
        with open(file_path, "wb") as f:
            chunk = audio_stream.read(1024)
            while chunk:
                f.write(chunk)
                chunk = audio_stream.read(1024)

        return file_path

    except (BotoCoreError, ClientError) as e:
        # Log or return None to indicate failure
        return None


if __name__ == "__main__":
    sample_text = "This is a test of your market bot voice system."
    path = text_to_speech(sample_text, "test_voice.mp3")
    print("Audio saved at:", path)