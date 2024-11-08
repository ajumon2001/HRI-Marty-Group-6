from openai import OpenAI
from pydub import AudioSegment

from dotenv import load_dotenv
load_dotenv()

def text_to_speech(text: str, voice: str = "alloy", output_file: str = "output.mp3", bitrate: str = "64k") -> None:
    """
    Convert text to speech using OpenAI's TTS API.
    
    Args:
        text (str): The text to convert to speech
        voice (str): The voice to use (alloy, echo, fable, onyx, nova, or shimmer)
        output_file (str): Path where the audio file will be saved
        
    Returns:
        None
    """
    try:
        client = OpenAI()
        
        # Create temporary file for initial output
        temp_file = "temp_output.mp3"
        
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        response.write_to_file(temp_file)
        
        # Compress the audio file
        audio = AudioSegment.from_mp3(temp_file)
        audio.export(output_file, format="mp3", bitrate=bitrate)
        
        # Clean up temporary file
        import os
        os.remove(temp_file)
        
    except Exception as e:
        raise Exception(f"Error during text-to-speech conversion: {str(e)}")


# if __name__ == "__main__":
#     from dotenv import load_dotenv
#     load_dotenv()
#     text_to_speech("Hello, how are you?", "echo", "output.mp3")