import time
import threading
from gpiozero import Motor

class SmoothedMotor:
    """
    A wrapper for the gpiozero.Motor class that provides gradual speed
    ramping (smoothing) to prevent sudden current spikes and back EMF.

    It accepts a target speed from -1.0 (full reverse) to 1.0 (full forward)
    and handles the transition in a background thread.
    """

    def __init__(self, *args, step_size=0.05, delay=0.02, **kwargs):
        """
        Initializes the smoothed motor.

        :param *args: Arguments to pass to the underlying gpiozero.Motor
                      (e.g., forward pin, backward pin).
        :param step_size: The amount to change the speed by in each step
                          (default: 0.05). A smaller value means a
                          slower, smoother ramp.
        :param delay: The time (in seconds) to wait between each speed
                      step (default: 0.02). A larger value means a
                      slower ramp.
        :param **kwargs: Keyword arguments to pass to gpiozero.Motor.
        """
        self.motor = Motor(*args, **kwargs)
        
        self.step_size = step_size
        self.delay = delay

        self.target_speed = 0.0
        self.current_speed = 0.0
        
        self._running = True
        self._lock = threading.Lock()
        
        # Start the background thread for speed ramping
        self.thread = threading.Thread(target=self._ramping_loop)
        self.thread.daemon = True  # Thread will exit when main program exits
        self.thread.start()

    def _ramping_loop(self):
        """Internal method run by the background thread."""
        while self._running:
            # Safely get the target and current speeds
            with self._lock:
                target = self.target_speed
                current = self.current_speed
            
            if current != target:
                # Calculate the new speed
                if target > current:
                    new_speed = min(current + self.step_size, target)
                else:
                    new_speed = max(current - self.step_size, target)
                
                # Apply the new speed to the motor
                if new_speed > 0:
                    self.motor.forward(new_speed)
                elif new_speed < 0:
                    self.motor.backward(abs(new_speed))
                else:
                    self.motor.stop()
                
                # Safely update the current speed
                with self._lock:
                    self.current_speed = new_speed
            
            # Wait for the next loop iteration
            time.sleep(self.delay)
        
        # Ensure motor is stopped when the loop exits
        self.motor.stop()

    def set_speed(self, speed):
        """
        Sets the target speed for the motor.

        :param speed: The desired speed, from -1.0 (full reverse)
                      to 1.0 (full forward).
        """
        # Clamp the speed to the valid range
        speed = max(-1.0, min(1.0, speed))
        
        # Safely update the target speed
        with self._lock:
            self.target_speed = speed

    def stop(self):
        """Gradually stops the motor."""
        self.set_speed(0.0)

    def close(self):
        """Stops the ramping thread and cleans up resources."""
        if self._running:
            self._running = False
            self.thread.join()  # Wait for the thread to finish
        self.motor.close()

    # --- Context Manager Support (`with` statement) ---
    
    def __enter__(self):
        """Allows the class to be used in a 'with' statement."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensures close() is called when exiting a 'with' block."""
        self.close()

# --- Example Usage ---
if __name__ == "__main__":
    # IMPORTANT: Replace 17 and 18 with the GPIO pins you
    # are using for your MDD3A motor driver (e.g., IN1 and IN2).
    
    # Using 'with' ensures that the .close() method is called
    # automatically, stopping the thread and cleaning up GPIO.
    
    # You would create one instance for each motor
    # motor_left = SmoothedMotor(LEFT_PIN_1, LEFT_PIN_2)
    # motor_right = SmoothedMotor(RIGHT_PIN_1, RIGHT_PIN_2)

    print("Running motor demonstration...")
    try:
        # These pins are just examples.
        with SmoothedMotor(17, 18) as motor1:
            
            print("Ramping to full forward (1.0)...")
            motor1.set_speed(1.0)
            time.sleep(3)  # Run at full speed for 3 seconds
            
            print("Ramping to half reverse (-0.5)...")
            motor1.set_speed(-0.5)
            time.sleep(3)  # Run at half reverse for 3 seconds
            
            print("Ramping to stop (0.0)...")
            motor1.stop()
            time.sleep(2)  # Wait for it to stop
            
            print("Demonstration complete.")

    except KeyboardInterrupt:
        print("\nExiting program.")
    
    finally:
        # This 'finally' block isn't strictly necessary when
        # using the 'with' statement, but shows how you would
        # manually clean up if not using 'with'.
        #
        # if 'motor1' in locals() and motor1._running:
        #     motor1.close()
        #     print("Motor resources cleaned up.")
        pass