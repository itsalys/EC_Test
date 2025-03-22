import Inp_Camera.facialRecognition as FR
import Inp_Mic.speechRecognition as SR
import Inp_Ultrasonic.objectDetection as UD
import time

def main():
    while True:
        distance = UD.measure_distance()
        print(f"Measured Distance: {distance} cm")

        if UD.is_object_in_range(distance, threshold=100):
            print("Object detected within 100 cm. Starting facial recognition...")
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
        else:
            print("No object detected within 100 cm. Skipping recognition cycle.")
            
        time.sleep(1)

if __name__ == "__main__":
    main()
