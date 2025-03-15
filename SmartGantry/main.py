import Inp_Camera.facialRecognition as FR
import Inp_Mic.speechRecognition as SR

def main():
    while True:
        user_input = input("Press 'g' to start facial recognition or 'q' to quit: ").strip().lower()

        if user_input == 'g':
            print("Trigger received. Initiating facial recognition...")
            result = FR.facialRecognition()  # Perform facial recognition

            if result:  # Check if a face was recognized
                wake_word = result["name"]
                print(f"User recognized: {wake_word} (ID: {result['id']}). Initiating speech recognition...")

                speech_detected = SR.speechRecognition(wake_word)

                if speech_detected:
                    print(f"Wake word '{wake_word}' detected. Proceeding with the next step.")
                else:
                    print("Wake word not detected. Restart the process if necessary.")
            else:
                print("Face not recognized. Please try again.")
        
        elif user_input == 'q':
            print("Exiting program.")
            break
        else:
            print("Invalid input. Please press 'g' to start or 'q' to quit.")

if __name__ == "__main__":
    main()
