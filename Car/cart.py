import socket, time
from gpiozero import PWMOutputDevice, DigitalOutputDevice, DistanceSensor, RGBLED

# GPIO pin setting
leftMotorSpeed = PWMOutputDevice(18)
leftMotorReverse = DigitalOutputDevice(22) #왼 바퀴 후진
leftMotorForward = DigitalOutputDevice(27) #왼 바퀴 전진
rightMotorSpeed = PWMOutputDevice(23)
rightMotorReverse = DigitalOutputDevice(25) #오른 바퀴 후진
rightMotorForward = DigitalOutputDevice(24) #오른 바퀴 전진

front_sensor = DistanceSensor(echo=10, trigger=9, max_distance=2.0)
left_sensor = DistanceSensor(echo=17, trigger=4, max_distance=2.0)
right_sensor = DistanceSensor(echo=8, trigger=7, max_distance=2.0)

# motor operation
def stop_motors():
    leftMotorSpeed.value = 0.0
    rightMotorSpeed.value = 0.0

def move_forward():
    leftMotorForward.value, leftMotorReverse.value = 1, 0
    rightMotorForward.value, rightMotorReverse.value = 1, 0
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

# udp setting
UDP_IP = "0.0.0.0"   # 모든 인터페이스에서 수신
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("UDP 서버 실행 중...")


while True:
    data, addr = sock.recvfrom(1024)  # (메시지, 송신자 주소)
    cmd = data.decode()
    print(f"수신: {cmd} from {addr}")

    front_distance = front_sensor.distance * 100
    left_distance = left_sensor.distance * 100
    right_distance = right_sensor.distance * 100


    if cmd == "forward":
        if front_distance > 30:
            if left_distance < 15 and right_distance < 15:
                stop_motors()
            elif right_distance < 15:
                while right_distance < 30:
                    turn_left_soft()
            elif left_distance < 15:
                while left_distance < 30:
                    turn_right_soft()
            else:
                move_forward()
        
        else:
            if left_distance > right_distance:
                turn_left_soft()
                time.sleep(1)
                move_forward()
                time.sleep(0.2)
            
            else:
                turn_right_soft()
                time.sleep(1)
                move_forward()
                time.sleep(0.2)

    elif cmd == "right":
        turn_right()

    elif cmd == "left":
        turn_left()
    
    elif cmd == "forward_close":
        stop_motors()

