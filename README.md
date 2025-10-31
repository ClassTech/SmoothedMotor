Raspberry Pi Smoothed Motor Controller
This project provides a simple Python wrapper class, SmoothedMotor, for the gpiozero.Motor class. Its primary purpose is to prevent Raspberry Pi crashes caused by back EMF (Electromotive Force) from brushed DC motors.

When a motor's speed changes suddenly (especially when stopping or reversing), it can send a voltage spike back to the motor driver (like an MDD3A) and the Raspberry Pi's GPIO pins, often causing a crash or reboot. This class solves the problem by implementing a gradual speed ramp, ensuring all speed changes are smooth.

⚙️ Key Features
Gradual Speed Ramping: Automatically ramps motor speed up and down to a target value.

Non-Blocking: Ramping is handled in a background thread, so your main code isn't blocked. You can set a new speed and your program continues immediately.

Simple Interface: Works just like gpiozero.Motor but accepts a target speed from -1.0 (full reverse) to 1.0 (full forward).

Drop-in Replacement: Designed to be easy to integrate into existing gpiozero projects.

🏁 Getting Started
Requirements

Python 3

gpiozero library (sudo apt install python3-gpiozero)

A Raspberry Pi

A motor driver (e.g., L298N, MDD3A, etc.) connected to your Raspberry Pi's GPIO pins.

Installation

There is no package to install. Simply download or copy the smoothed_motor.py file and place it in the same directory as your main Python script.

How to Use

Import the class and instantiate it just like you would a gpiozero.Motor, providing the forward and backward GPIO pins.

Python
from smoothed_motor import SmoothedMotor
from time import sleep

# Use the GPIO pins connected to your motor driver's
# IN1 and IN2 (or equivalent) pins.
# These are just examples! Change them to your pins.
PIN_A = 17
PIN_B = 18

try:
    # 'with' statement is recommended!
    with SmoothedMotor(PIN_A, PIN_B) as motor:
        
        print("Ramping to 80% forward...")
        motor.set_speed(0.8)
        sleep(3) # Motor will ramp up and run while this sleeps

        print("Ramping to 50% reverse...")
        motor.set_speed(-0.5)
        sleep(3)
        
        print("Stopping...")
        motor.stop() # Ramps down to 0.0
        sleep(2)

except KeyboardInterrupt:
    print("Program stopped.")

Advanced Usage
Tuning the Ramp Speed

You can customize the smoothness of the ramp by passing two optional parameters during initialization:

step_size: The amount to change the speed by in each step. (Default: 0.05)

delay: The time (in seconds) to wait between each step. (Default: 0.02)

Example for a much slower, smoother ramp: (Good for heavy motors or very sensitive power supplies)

Python
# This ramp will be much more gradual
motor = SmoothedMotor(17, 18, step_size=0.01, delay=0.05)
Context Manager (with statement)

It is highly recommended to use the class within a with statement, as shown in the main example.

Python
with SmoothedMotor(17, 18) as motor:
    # Your code here
    
# When your code leaves the 'with' block (even if an error occurs),
# the motor.close() method is automatically called.
This ensures that the background ramping thread is stopped cleanly and the GPIO resources are released, preventing errors.

If you cannot use a with statement, you must manually call the close() method when your program is done.

Python
motor = SmoothedMotor(17, 18)
try:
    # Your code here
    motor.set_speed(0.5)
    sleep(1)
finally:
    # This is crucial!
    motor.close()
    print("Motor resources cleaned up.")