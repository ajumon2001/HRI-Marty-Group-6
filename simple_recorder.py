import sounddevice as sd
import numpy as np
from pydub import AudioSegment
import io
import wave
import time

def record_audio(duration=5, sample_rate=44100, silence_threshold=-40, silence_duration=2):
    """Record audio until silence is detected or max duration is reached"""
    print(f"Recording... (max duration: {duration} seconds)")
    
    # Calculate parameters
    chunk_duration = 0.1  # Process audio in 100ms chunks
    chunk_samples = int(chunk_duration * sample_rate)
    total_chunks = int(duration / chunk_duration)
    chunks = []
    silent_chunks = 0
    max_silent_chunks = int(silence_duration / chunk_duration)
    
    # Create a stream for continuous recording
    stream = sd.InputStream(samplerate=sample_rate, channels=1, dtype=np.int16)
    stream.start()
    
    try:
        start_time = time.time()
        while time.time() - start_time < duration:
            # Read chunk from stream
            chunk, _ = stream.read(chunk_samples)
            chunk = chunk.reshape(-1)  # Ensure proper shape
            
            # Convert to float and calculate RMS
            chunk_float = chunk.astype(np.float32) / 32768.0
            rms = 20 * np.log10(np.sqrt(np.mean(chunk_float**2)) + 1e-10)
            
            # Check if chunk is silent
            if rms < silence_threshold:
                silent_chunks += 1
                if silent_chunks >= max_silent_chunks:
                    print("Silence detected, stopping recording...")
                    break
            else:
                silent_chunks = 0
                
            chunks.append(chunk)
            
    finally:
        stream.stop()
        stream.close()
    
    if not chunks:
        raise ValueError("No audio recorded!")
        
    # Combine all chunks
    recording = np.concatenate(chunks, axis=0)
    print("Recording finished!")
    print(f"Recorded {len(recording) / sample_rate:.2f} seconds of audio")
    
    # First save as WAV using wave module
    with io.BytesIO() as wav_io:
        with wave.open(wav_io, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit audio
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(recording.tobytes())
        
        # Convert WAV to AudioSegment
        wav_io.seek(0)
        audio_segment = AudioSegment.from_wav(wav_io)
    
    # Export as MP3
    audio_segment.export("recording.mp3", format="mp3")
    print("Saved as recording.mp3")

    return recording, sample_rate

# if __name__ == "__main__":
#     # Make sure you have ffmpeg installed for MP3 conversion
#     try:
#         recording, sample_rate = record_audio(
#             duration=50,
#             sample_rate=44100,
#             silence_threshold=-40,
#             silence_duration=2
#         )
#     except Exception as e:
#         print(f"Error occurred: {str(e)}")