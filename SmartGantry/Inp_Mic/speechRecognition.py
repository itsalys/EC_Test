import speech_recognition as sr
import time
import os

def speechRecognition(wake_word):
    """
    Listens for speech input and checks if the wake word is detected.
    
    :param wake_word: The word to listen for.
    :return: True if the wake word is detected, False otherwise.
    """
    r = sr.Recognizer()  # Initialize Recognizer
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)  # Adapt to ambient noise
        os.system('clear') 
        print(f"Speech Recognition - Listening for wake word: {wake_word} ...")
        
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print("Speech Recognition - Timeout: No speech detected within the time limit.")
            return False


    # Recognize speech using Google Speech Recognition
    start_time = time.time()
    try:
        text = r.recognize_google(audio).lower()  # Convert speech to lowercase text
        print(f"Speech Recognition - Recognized: {text}")
        if wake_word.lower() in text:  # Check if wake word is in recognized text
            print("Speech Recognition - Wake word detected!")
            return True
        else:
            print("Speech Recognition - Wake word not detected.")
            return False
    except sr.UnknownValueError:
        print("Speech Recognition - Could not understand audio.")
    except sr.RequestError as e:
        print(f"Speech Recognition - Error connecting to Google Speech Recognition service: {e}")

    print(f"Speech Recognition - Recognition time: {time.time() - start_time:.0f} seconds")
    return False  # Return False if an error occurs

# Example usage
if __name__ == "__main__":
    wake_word = "hello"  # Change this to your desired wake word
    result = speechRecognition(wake_word)
    print(f"Speech Recognition - Wake word detected: {result}")
