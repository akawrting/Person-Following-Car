from flask import Flask, Response, render_template, request
from picamera2 import Picamera2
import socket, time, threading, cv2
from gpiozero import PWMOutputDevice, DigitalOutputDevice, DistanceSensor, RGBLED
import motor


front_sensor = DistanceSensor(echo=10, trigger=9, max_distance=2.0)
left_sensor = DistanceSensor(echo=17, trigger=4, max_distance=2.0)
right_sensor = DistanceSensor(echo=8, trigger=7, max_distance=2.0)



def auto_following():
    global auto_mode

    sock.settimeout(0.1) 

    while True:
        if not auto_mode:
            time.sleep(0.1)
            continue

        try:
            data, addr = sock.recvfrom(1024)
        except socket.timeout:
            continue

        yolo_cmd = data.decode()
        print("yolo command:", yolo_cmd)

        front_distance = front_sensor.distance * 100
        left_distance = left_sensor.distance * 100
        right_distance = right_sensor.distance * 100

        if yolo_cmd == "forward":
            if front_distance > 30:
                if left_distance < 15 and right_distance < 15:
                    motor.stop_motors()
                elif right_distance < 30:
                        motor.turn_left_soft()
                elif left_distance < 30:
                        motor.turn_right_soft()
                else:
                    motor.move_forward()
            
            else:
                if left_distance > right_distance:
                    motor.turn_left_soft()
                    time.sleep(1)
                    motor.move_forward()
                    time.sleep(0.2)
                
                else:
                    motor.turn_right_soft()
                    time.sleep(1)
                    motor.move_forward()
                    time.sleep(0.2)

        elif yolo_cmd == "right":
            motor.turn_right_soft()
        elif yolo_cmd == "left":
            motor.turn_left_soft()

        elif yolo_cmd == "forward_close":
            motor.stop_motors()


auto_mode = False

app = Flask(__name__)

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (1280, 720)}))
camera.start()


# udp setting
UDP_IP = "0.0.0.0"   
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print("UDP server activated")

thread_1 = threading.Thread(target = auto_following)
thread_1.start()

def generate_frames():
    while True:
        frame = camera.capture_array()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/control')
def show_buttons():
    return render_template('control.html')

@app.route('/control/<web_cmd>', methods=['POST'])
def control(web_cmd):
    global auto_mode
    print("web command:", web_cmd)

    if web_cmd == 'forward':
        motor.move_forward()
        print("forward")
    elif web_cmd == 'backward':
        motor.move_backward()
        print("backward")
    elif web_cmd == 'left':
        motor.turn_left_soft()
        print("left")
    elif web_cmd == 'right':
        motor.turn_right_soft()
        print("right")
    elif web_cmd == 'stop':
        motor.stop_motors()
        print("stop")
    elif web_cmd == 'power':
        if not auto_mode:
            auto_mode = True
            print("auto mode on")
        else:
            auto_mode = False
            time.sleep(0.2)
            motor.stop_motors()
            print("auto mode off")

    return "OK"

@app.route('/mode', methods=['POST'])
def mode():
    global auto_mode

    value = request.form.get('value')  # "1" 또는 "0"
    auto_mode = bool(int(value))
    if auto_mode == False:
        time.sleep(0.2)
        motor.stop_motors()
    print("현재 auto_mode:", auto_mode)
    return "OK"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 