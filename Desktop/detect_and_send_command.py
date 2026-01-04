import cv2
import torch
from ultralytics import YOLO
import numpy as np
import requests
import socket

UDP_IP = "192.168.0.3"  # Car ip
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# MJPEG 스트리밍 URL
url = "http://192.168.0.3:5000/video_feed"  # Car_ip/video_feed
stream = requests.get(url, stream=True)

# YOLO 모델 로딩
model = YOLO("yolo11n.pt")
model.conf = 0.4

bytes_buffer = b""
for chunk in stream.iter_content(chunk_size=1024):
    bytes_buffer += chunk
    a = bytes_buffer.find(b'\xff\xd8')  # JPEG 시작
    b = bytes_buffer.find(b'\xff\xd9')  # JPEG 끝

    if a != -1 and b != -1 and a < b:
        jpg = bytes_buffer[a:b+2]
        bytes_buffer = bytes_buffer[b+2:]

        frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

        if frame is None:
            continue

        # YOLO 추론 실행
        results = model(frame)

        
        for result in results:
            boxes = result.boxes.xyxy
            confidences = result.boxes.conf
            classes = result.boxes.cls

            for box, conf, cls in zip(boxes, confidences, classes):
                if int(cls) == 0:       # 사람만 필터링 (Class ID: 0)
                    x1, y1, x2, y2 = map(int, box)
                    cx = x1 + (x2 - x1) / 2
                    # 메세지 전송
                    if cx < 400:
                        msg = "left"
                    elif cx < 800:
                        if y1 > 50:
                            msg = "forward"
                        else: 
                            msg = "forward_close"
                    elif cx < 1280:
                        msg = "right"
                    sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))

                    label = f"Person {conf:.2f} x={cx} y={y1}"
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 결과 출력
        cv2.imshow("Person Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
