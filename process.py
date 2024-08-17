import os
import sys
import cv2
from ultralytics import YOLO


class Processor:
    __current_model: str
    model: YOLO

    def __init__(self, model: str):
        base_path = os.path.join(os.path.abspath('.'), 'modelos')
        self.model = YOLO(os.path.join(base_path, f'{model}.pt'))
        self.__current_model = model


    def process_video(self, video_path) -> bool :
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Error opening video stream or file")
            return False

        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                results = self.model(frame)
                if len(results[0].boxes.cls) > 1:
                    cap.release()
                    return True
            else:
                break

        cap.release()
        return True