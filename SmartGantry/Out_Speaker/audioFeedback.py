import pyaudio
import wave
import time

# Define file paths for the audio messages
SUCCESS_AUDIO = "Out_Speaker/success.wav"  # Replace with your actual success message file
DENIED_AUDIO = "Out_Speaker/error.wav"     # Replace with your actual denied message file
ERROR_AUDIO = "Out_Speaker/error.wav"      # Replace with your actual error message file

def play_audio(file_path):
    """Plays the given audio file."""
    try:
        wf = wave.open(file_path, 'rb')
        audio = pyaudio.PyAudio()

        BUFFER = 4096

        stream = audio.open(
            format=audio.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
            frames_per_buffer=BUFFER,
        )

        data = wf.readframes(BUFFER)

        while data:
            stream.write(data)
            data = wf.readframes(BUFFER)

        # Clean up
        stream.stop_stream()
        stream.close()
        audio.terminate()
        wf.close()

    except FileNotFoundError:
        print(f"Audio Feedback - Error: File {file_path} not found.")
    except Exception as e:
        print(f"Audio Feedback - An error occurred while playing {file_path}: {e}")

def play_success_message():
    """Plays the success message."""
    print("Audio Feedback - Playing success message...")
    play_audio(SUCCESS_AUDIO)

def play_denied_message():
    """Plays the denied message."""
    print("Audio Feedback - Playing denied message...")
    play_audio(DENIED_AUDIO)

def play_error_message():
    """Plays the error message."""
    print("Audio Feedback - Playing error message...")
    play_audio(ERROR_AUDIO)

if __name__ == "__main__":
    """Main function to test the audio messages."""
    print("Audio Feedback - Starting audio tests...")

    play_success_message()
    time.sleep(1)

    play_denied_message()
    time.sleep(1)

    play_error_message()

    print("Audio Feedback - Audio tests completed.")
