import time
from smoothed_motor import SmoothedMotor

# --- ! IMPORTANT ! ---
# Change these pin numbers to match your Raspberry Pi's
# connections to your MDD3A motor driver.
# Using GPIO numbering.

# Pins for Motor 1 (e.g., IN1 and IN2)
MOTOR_1_FWD_PIN = 17  # CHANGE THIS
MOTOR_1_REV_PIN = 18  # CHANGE THIS

# Pins for Motor 2 (e.g., IN3 and IN4)
MOTOR_2_FWD_PIN = 27  # CHANGE THIS
MOTOR_2_REV_PIN = 22  # CHANGE THIS

# ----------------------------------------------------


def run_motor_test():
    print("Starting motor test sequence...")
    
    # Using 'with' statements ensures that the motor.close()
    # method is called automatically to clean up the threads
    # and GPIO pins, even if an error occurs.
    try:
        with SmoothedMotor(MOTOR_1_FWD_PIN, MOTOR_1_REV_PIN) as motor1, \
             SmoothedMotor(MOTOR_2_FWD_PIN, MOTOR_2_REV_PIN) as motor2:

            # --- 1. RAMP TO FULL FORWARD ---
            print("Ramping to 100% FORWARD...")
            motor1.set_speed(1.0)
            motor2.set_speed(1.0)
            
            # Run at this speed for 3 seconds.
            # The ramping happens in the background.
            print("Running forward for 3 seconds...")
            time.sleep(3.0)

            # --- 2. RAMP TO FULL REVERSE ---
            print("Ramping to 100% REVERSE...")
            motor1.set_speed(-1.0)
            motor2.set_speed(-1.0)
            
            # Run at this speed for 3 seconds.
            print("Running reverse for 3 seconds...")
            time.sleep(3.0)

            # --- 3. RAMP TO STOP ---
            print("Ramping to STOP...")
            motor1.stop()
            motor2.stop()
            
            # IMPORTANT: Wait for the motors to ramp down to 0
            # before the 'with' block ends and calls .close()
            # The default ramp (1.0 -> 0.0) takes ~0.4s.
            # We'll wait 1 second to be safe.
            print("Waiting for ramp-down...")
            time.sleep(1.0)
            
            print("Motor test complete.")

    except KeyboardInterrupt:
        # This allows you to press Ctrl+C to stop the test
        print("\nTest interrupted by user. Motors will be stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Ensure GPIO pins are correct and you are running as a user")
        print("with GPIO permissions (or use 'sudo').")

if __name__ == "__main__":
    run_motor_test()