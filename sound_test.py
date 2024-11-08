import sounddevice as sd
import numpy as np
import webrtcvad
import wave
import keyboard
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class RecorderConfig:
    """Configuration settings for the voice recorder"""
    sample_rate: int = 16000
    chunk_duration_ms: int = 30
    vad_aggressiveness: int = 3
    silence_threshold: int = 30
    stop_key: str = 'esc'

class AudioProcessor:
    """Handles audio processing operations"""
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.vad = webrtcvad.Vad(3)
    
    def convert_to_int16(self, float32_data: np.ndarray) -> np.ndarray:
        """Convert float32 audio data to int16"""
        return (float32_data * 32767).astype(np.int16)
    
    def is_speech(self, audio_data: np.ndarray) -> bool:
        """Detect if audio chunk contains speech"""
        try:
            return self.vad.is_speech(audio_data.tobytes(), self.sample_rate)
        except:
            return False

class AudioSaver:
    """Handles saving audio to files"""
    @staticmethod
    def save_to_wav(filename: str, audio_data: np.ndarray, sample_rate: int) -> None:
        """Save audio data to WAV file"""
        if audio_data is None:
            print("No audio data to save")
            return
            
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())
        print(f"Recording saved to {filename}")

class VoiceRecorder:
    """Main voice recorder class with speech detection and manual stop capability"""
    
    def __init__(self, config: RecorderConfig = RecorderConfig()):
        self.config = config
        self.chunk_size = int(config.sample_rate * config.chunk_duration_ms / 1000)
        self.audio_processor = AudioProcessor(config.sample_rate)
        self.reset_state()
        
    def reset_state(self) -> None:
        """Reset all recording state variables"""
        self.recorded_data: List[np.ndarray] = []
        self.silent_chunks = 0
        self.speech_detected = False
        self.should_stop = False
        
    def stop_recording(self) -> None:
        """Stop the recording when called"""
        self.should_stop = True
        print("\nStopping recording...")
        
    def setup_keyboard_listener(self) -> None:
        """Set up the keyboard listener for manual stop"""
        keyboard.on_press_key(
            self.config.stop_key, 
            lambda _: self.stop_recording()
        )
        
    def cleanup_keyboard_listener(self) -> None:
        """Clean up keyboard listener"""
        keyboard.unhook_all()
        
    def process_audio_chunk(self, indata: np.ndarray) -> bool:
        """Process a chunk of audio data and return True if recording should stop"""
        # Convert audio format
        audio_chunk = self.audio_processor.convert_to_int16(indata)
        
        # Check for speech
        if self.audio_processor.is_speech(audio_chunk):
            self.speech_detected = True
            self.silent_chunks = 0
            self.recorded_data.append(audio_chunk.copy())
        elif self.speech_detected:
            self.silent_chunks += 1
            self.recorded_data.append(audio_chunk.copy())
            
        # Check if we should stop due to silence
        if self.silent_chunks > self.config.silence_threshold:
            print("\nSilence detected, stopping recording...")
            return True
            
        return False
        
    def audio_callback(self, indata: np.ndarray, frames: int, time: any, status: any) -> None:
        """Callback function for audio stream"""
        if status:
            print(status)
            
        if self.should_stop or self.process_audio_chunk(indata):
            raise sd.CallbackStop()
            
    def record(self) -> Optional[np.ndarray]:
        """Record audio until silence is detected or stop key is pressed"""
        print(f"Listening... Speak now (press '{self.config.stop_key}' to stop manually or wait for silence)")
        self.reset_state()
        self.setup_keyboard_listener()
        
        try:
            with sd.InputStream(
                samplerate=self.config.sample_rate,
                channels=1,
                callback=self.audio_callback,
                dtype=np.float32,
                blocksize=self.chunk_size
            ):
                while True:
                    sd.sleep(100)
        except sd.CallbackStop:
            pass
        finally:
            self.cleanup_keyboard_listener()
            
        # Modified this part to handle empty data and ensure proper concatenation
        if not self.recorded_data:
            return None
        try:
            return np.concatenate(self.recorded_data, axis=0)  # Changed from vstack to concatenate
        except ValueError:
            print("Error concatenating audio data")
            return None



# # Create custom configuration if needed
# config = RecorderConfig(
#     sample_rate=16000,
#     chunk_duration_ms=30,
#     silence_threshold=30,
#     stop_key='esc'
# )

# # Initialize and use recorder
# recorder = VoiceRecorder(config)
# audio_data = recorder.record()

# # Save recording if we have data
# if audio_data is not None:
#     saver = AudioSaver()
#     saver.save_to_wav("recording.wav", audio_data, config.sample_rate)

