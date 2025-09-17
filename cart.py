import socket
from gpiozero import PWMOutputDevice, DigitalOutputDevice, DistanceSensor, RGBLED

# GPIO pin setting
PWMA = PWMOutputDevice(18)
AIN1 = DigitalOutputDevice(22) #왼 바퀴 후진
AIN2 = DigitalOutputDevice(27) #왼 바퀴 전진
PWMB = PWMOutputDevice(23)
BIN1 = DigitalOutputDevice(25) #오른 바퀴 후진
BIN2 = DigitalOutputDevice(24) #오른 바퀴 전진

front_sensor = DistanceSensor(echo=10, trigger=9, max_distance=2.0)
left_sensor = DistanceSensor(echo=17, trigger=4, max_distance=2.0)
right_sensor = DistanceSensor(echo=8, trigger=7, max_distance=2.0)

# motor operation
def stop_motors():
    PWMA.value = 0.0
    PWMB.value = 0.0

def move_forward():
    AIN1.value, AIN2.value = 0, 1
    BIN1.value, BIN2.value = 0, 1
    PWMA.value = 1
    PWMB.value = 1

def turn_left():
    AIN1.value, AIN2.value = 1, 0
    BIN1.value, BIN2.value = 0, 1
    PWMA.value = 0.4
    PWMB.value = 0.4

def turn_right():
    AIN1.value, AIN2.value = 0, 1
    BIN1.value, BIN2.value = 1, 0
    PWMA.value = 0.4
    PWMB.value = 0.4

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

    if front_distance > 30:
        print(front_distance)
        if cmd == "left":
            print("동작 A 실행")
            turn_left()
        elif cmd == "forward":
            print("동작 B 실행")
            move_forward()
        elif cmd == "right":
            print("동작 C 실행")
            turn_right()
        elif cmd == "stop":
            print("stop")
            stop_motors()
        elif cmd == "q":
            print("종료 명령 수신")
            break
    elif front_distance <= 30:
        stop_motors()
