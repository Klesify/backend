"""
Audio Transcription Module
Converts audio blobs (recordings) from phone calls into text for fraud analysis.
"""

import os
from typing import Optional, Union, BinaryIO
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def transcribe_audio_blob(
    audio_data: Union[bytes, BinaryIO, str],
    audio_format: str = "mp3",
    language: str = "ro",
    model: str = "whisper-1"
) -> Optional[str]:
    """
    Transcribe audio blob from phone call into text using OpenAI Whisper.
    
    Args:
        audio_data: Audio data as bytes, file-like object, or file path
        audio_format: Audio format (mp3, wav, m4a, webm, etc.)
        language: Language code (ro for Romanian, en for English, etc.)
        model: Whisper model to use (default: whisper-1)
        
    Returns:
        str: Transcribed text, or None if transcription fails
        
    Examples:
        # From bytes
        with open("call.mp3", "rb") as f:
            audio_bytes = f.read()
        text = transcribe_audio_blob(audio_bytes)
        
        # From file path
        text = transcribe_audio_blob("path/to/call.mp3")
        
        # From file object
        with open("call.mp3", "rb") as f:
            text = transcribe_audio_blob(f)
    """
    
    try:
        # Handle different input types
        if isinstance(audio_data, str):
            # It's a file path
            with open(audio_data, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                    language=language,
                    response_format="text"
                )
        elif isinstance(audio_data, bytes):
            # It's raw bytes - need to create a file-like object
            import io
            audio_file = io.BytesIO(audio_data)
            audio_file.name = f"audio.{audio_format}"
            
            transcript = client.audio.transcriptions.create(
                model=model,
                file=audio_file,
                language=language,
                response_format="text"
            )
        else:
            # It's already a file-like object
            if not hasattr(audio_data, 'name'):
                audio_data.name = f"audio.{audio_format}"
                
            transcript = client.audio.transcriptions.create(
                model=model,
                file=audio_data,
                language=language,
                response_format="text"
            )
        
        return transcript
        
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None


def transcribe_audio_with_timestamps(
    audio_data: Union[bytes, BinaryIO, str],
    audio_format: str = "mp3",
    language: str = "ro"
) -> Optional[dict]:
    """
    Transcribe audio with detailed timestamps and segments.
    
    Args:
        audio_data: Audio data as bytes, file-like object, or file path
        audio_format: Audio format (mp3, wav, m4a, webm, etc.)
        language: Language code (ro for Romanian, en for English, etc.)
        
    Returns:
        dict: Detailed transcription with segments and timestamps
        {
            "text": "full transcription",
            "segments": [
                {
                    "start": 0.0,
                    "end": 5.2,
                    "text": "segment text"
                },
                ...
            ],
            "duration": 120.5
        }
    """
    
    try:
        # Handle different input types
        if isinstance(audio_data, str):
            with open(audio_data, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json"
                )
        elif isinstance(audio_data, bytes):
            import io
            audio_file = io.BytesIO(audio_data)
            audio_file.name = f"audio.{audio_format}"
            
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json"
            )
        else:
            if not hasattr(audio_data, 'name'):
                audio_data.name = f"audio.{audio_format}"
                
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_data,
                language=language,
                response_format="verbose_json"
            )
        
        # Convert to dict format
        result = {
            "text": transcript.text,
            "segments": [
                {
                    "start": segment.start if hasattr(segment, 'start') else 0,
                    "end": segment.end if hasattr(segment, 'end') else 0,
                    "text": segment.text if hasattr(segment, 'text') else ""
                }
                for segment in transcript.segments
            ] if hasattr(transcript, 'segments') else [],
            "duration": transcript.duration if hasattr(transcript, 'duration') else 0,
            "language": transcript.language if hasattr(transcript, 'language') else language
        }
        
        return result
        
    except Exception as e:
        print(f"Error transcribing audio with timestamps: {e}")
        return None


def save_audio_blob(audio_data: bytes, output_path: str) -> bool:
    """
    Save audio blob to file for processing or debugging.
    
    Args:
        audio_data: Raw audio bytes
        output_path: Path where to save the audio file
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        with open(output_path, "wb") as f:
            f.write(audio_data)
        return True
    except Exception as e:
        print(f"Error saving audio blob: {e}")
        return False
