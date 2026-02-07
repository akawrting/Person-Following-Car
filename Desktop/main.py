from ultralytics import YOLO

import time
import torch
import cv2
import torch.backends.cudnn as cudnn
from PIL import Image
import colorsys
import numpy as np
import socket
import os
import threading

from Tracking_Using_DeepSORT.deep_sort.utils.parser import get_config
from Tracking_Using_DeepSORT.deep_sort.deep_sort import DeepSort
from Tracking_Using_DeepSORT.deep_sort.sort.tracker import Tracker

# UDP setting
Car_IP = "192.168.0.3"  
PC_to_Car_PORT = 5005
Car_to_PC_PORT = 5006
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", Car_to_PC_PORT))

def reset_id():
    while True:
        try:
            data, addr = sock.recvfrom(1024)
        except socket.timeout:
            return
        cmd = data.decode()

        if cmd == "reset":
            tracker.tracker.reset_id()
            tracker.tracker.tracks.clear()

thread_1 = threading.Thread(target = reset_id)
thread_1.start()



deep_sort_weights = 'Tracking_Using_DeepSORT/deep_sort/deep/checkpoint/ckpt.t7'
tracker = DeepSort(model_path=deep_sort_weights, max_age=70)

# Define the video path
video_path = 'http://192.168.0.3:5000/video_feed'

cap = cv2.VideoCapture(video_path)

# Get the video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)


device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')


unique_track_ids = set()

i = 0
counter, fps, elapsed = 0, 0, 0
start_time = time.perf_counter()
model = YOLO("yolo11s.pt")  # load a pretrained model (recommended for training)

while cap.isOpened():
    ret, frame = cap.read()

    if ret:
        
        og_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = og_frame.copy()

        

        results = model(frame, device=0, classes=0, conf=0.8)

        class_names = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']

        for result in results:
            boxes = result.boxes  # Boxes object for bbox outputs
            probs = result.probs  # Class probabilities for classification outputs
            cls = boxes.cls.tolist()  # Convert tensor to list
            xyxy = boxes.xyxy
            conf = boxes.conf
            xywh = boxes.xywh  # box with xywh format, (N, 4)
            for class_index in cls:
                class_name = class_names[int(class_index)]
                #print("Class:", class_name)

        pred_cls = np.array(cls)
        conf = conf.detach().cpu().numpy()
        xyxy = xyxy.detach().cpu().numpy()
        bboxes_xywh = xywh
        bboxes_xywh = xywh.cpu().numpy()
        bboxes_xywh = np.array(bboxes_xywh, dtype=float)
        
        tracks = tracker.update(bboxes_xywh, conf, og_frame)
        
        for track in tracker.tracker.tracks:
            track_id = track.track_id
            
            hits = track.hits
            x1, y1, x2, y2 = track.to_tlbr()  # Get bounding box coordinates in (x1, y1, x2, y2) format
            w = x2 - x1  # Calculate width
            h = y2 - y1  # Calculate height
            
            if track_id == 1:
                cx = x1 + (x2 - x1) / 2
                if cx < 400:
                        msg = "left"
                elif cx < 800:
                    if y1 > 50:
                        msg = "forward"
                    else: 
                        msg = "forward_close"
                elif cx < 1280:
                    msg = "right"
                sock.sendto(msg.encode(), (Car_IP, PC_to_Car_PORT))

            # Set color values for red, blue, and green
            red_color = (0, 0, 255)  # (B, G, R)
            blue_color = (255, 0, 0)  # (B, G, R)
            green_color = (0, 255, 0)  # (B, G, R)

            # Determine color based on track_id
            color_id = track_id % 3
            if color_id == 0:
                color = red_color
            elif color_id == 1:
                color = blue_color
            else:
                color = green_color

            
            label = f"x1={x1} x2={x2} y1={y1} y2={y2} cx={cx}"
            cv2.rectangle(og_frame, (int(x1), int(y1)), (int(x1 + w), int(y1 + h)), color, 2)

            text_color = (0, 0, 0)  # Black color for text
            cv2.putText(og_frame, f"{class_name}-{track_id}", (int(x1) + 10, int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)
            # Add the track_id to the set of unique track IDs
            unique_track_ids.add(track_id)

        # Update the person count based on the number of unique track IDs
        person_count = len(unique_track_ids)

        # Update FPS and place on frame
        current_time = time.perf_counter()
        elapsed = (current_time - start_time)
        counter += 1
        if elapsed > 1:
            fps = counter / elapsed
            counter = 0
            start_time = current_time


        #Show the frame
        cv2.imshow("Video", og_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()