import whisper
import os

def transcribe_audio(audio_file_path: str, model_name: str = "base") -> str:
    """
    Transcribe an audio file using OpenAI's Whisper model.
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe
        model_name (str): Whisper model to use (tiny, base, small, medium, large)
    
    Returns:
        str: Transcribed text from the audio file
    
    Raises:
        FileNotFoundError: If the audio file doesn't exist
        ValueError: If the audio file format is not supported
    """
    # Check if file exists
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    # Check file extension
    if not audio_file_path.lower().endswith('.mp3'):
        raise ValueError("File must be an MP3 file")
    
    try:
        # Load the Whisper model
        model = whisper.load_model(model_name)
        
        # Transcribe the audio
        result = model.transcribe(audio_file_path)
        
        # Return the transcribed text
        return result["text"]
    
    except Exception as e:
        raise Exception(f"Error during transcription: {str(e)}")

# Example usage:
# if __name__ == "__main__":
#     try:
#         audio_path = "./recording.mp3"
#         transcription = transcribe_audio(audio_path)
#         print("Transcription:")
#         print(transcription)
#     except Exception as e:
#         print(f"Error: {str(e)}")
