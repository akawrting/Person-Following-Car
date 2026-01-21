from gpiozero import PWMOutputDevice, DigitalOutputDevice

# GPIO pin setting
leftMotorSpeed = PWMOutputDevice(18)
leftMotorReverse = DigitalOutputDevice(22) 
leftMotorForward = DigitalOutputDevice(27) 
rightMotorSpeed = PWMOutputDevice(23)
rightMotorReverse = DigitalOutputDevice(25)
rightMotorForward = DigitalOutputDevice(24)

# motor operation
def stop_motors():
    leftMotorSpeed.value = 0.0
    rightMotorSpeed.value = 0.0

def move_forward():
    leftMotorForward.value, leftMotorReverse.value = 1, 0
    rightMotorForward.value, rightMotorReverse.value = 1, 0
    leftMotorSpeed.value = 1
    rightMotorSpeed.value = 1

def move_backward():
    leftMotorForward.value, leftMotorReverse.value = 0, 1
    rightMotorForward.value, rightMotorReverse.value = 0, 1
    leftMotorSpeed.value = 1
    rightMotorSpeed.value = 1

def turn_left_soft():
    leftMotorForward.value, leftMotorReverse.value = 0, 0
    rightMotorForward.value, rightMotorReverse.value = 1, 0
    leftMotorSpeed.value = 1
    rightMotorSpeed.value = 1

def turn_right_soft():
    leftMotorForward.value, leftMotorReverse.value = 1, 0
    rightMotorForward.value, rightMotorReverse.value = 0, 0
    leftMotorSpeed.value = 1
    rightMotorSpeed.value = 1 

def turn_left():
    leftMotorForward.value, leftMotorReverse.value = 0, 1
    rightMotorForward.value, rightMotorReverse.value = 1, 0
    leftMotorSpeed.value = 0.4
    rightMotorSpeed.value = 0.4

def turn_right():
    leftMotorForward.value, leftMotorReverse.value = 1, 0
    rightMotorForward.value, rightMotorReverse.value = 0, 1
    leftMotorSpeed.value = 0.4
    rightMotorSpeed.value = 0.4