import RPi.GPIO as GPIO
import time

# Define GPIO pins
TRIG = 23
ECHO = 24

# Setup GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def measure_distance():
    """
    Measures the distance using the ultrasonic sensor.
    Returns the distance in centimeters.
    """
    GPIO.output(TRIG, False)
    time.sleep(0.1)  # Short delay for sensor stability

    # Send trigger pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Wait for echo response
    pulse_start = time.time()
    timeout_start = time.time()
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if pulse_start - timeout_start > 0.02:  # Timeout after 20ms
            return -1  # No valid measurement

    pulse_end = time.time()
    timeout_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if pulse_end - timeout_start > 0.02:  # Timeout after 20ms
            return -1

    # Calculate distance
    pulse_duration = pulse_end - pulse_start
    distance = (pulse_duration * 34300) / 2  # Speed of sound in air: 343m/s
    return round(distance, 2)

def is_object_in_range(distance, threshold=10):
    """
    Checks if an object is within a given range.
    :param distance: Distance measured by the sensor.
    :param threshold: Detection range in cm (default = 10cm).
    :return: True if an object is within range, else False.
    """
    if distance == -1:
        print("Object Detection - Error: No valid measurement received.")
        return False
    return distance <= threshold


# Run the main function
if __name__ == "__main__":
    """
    Main function to continuously check for objects in range.
    """
    try:
        while True:
            distance = measure_distance()
            print(f"Object Detection - Measured Distance: {distance} cm")

            if is_object_in_range(distance, threshold=50):
                print("Object Detection - Object Detected in Range!")
            else:
                print("Object Detection - No Object Detected.")

            time.sleep(1)  # Wait before next measurement

    except KeyboardInterrupt:
        print("\nObject Detection - Measurement stopped by user.")
        GPIO.cleanup()
