import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator  # ultralytics.yolo.utils.plotting is deprecated
import pandas
import keyboard
import mss

bounding_box = {'top': 100, 'left': 0, 'width': 400, 'height': 300}

class Vision():
    def __init__(self):
        self.display = mss.mss()
        self.model = YOLO("best.pt")
        self.bounding_box = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
        self.currentBox = []

    def ReturnAllChordinates(self):
        frame = self.display.grab(self.bounding_box)
        
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_BGRA2BGR)
        labels = self.model.predict(source = frame, conf = .50, save = False)

        labels = self.model(frame)

    

        return labels[0].boxes

    def twoClosestCones(self):  # Uses the cone size to find the two closest cone
        lastKey = False
        while not lastKey:
            frame = self.display.grab(self.bounding_box)
            frame = cv2.cvtColor(np.array(frame), cv2.COLOR_BGRA2BGR)
            labels = self.model.predict(source = frame, conf = .50, save = False, verbose = False)

            biggest = []
            for r in labels: 
                boxes = r.boxes

                for box in boxes:
                    b = box.xyxy[0] #(top-Left x) (top-Left Y) (Bottom-Right x) (Bottom-Right y))
                    print(b)
                    c = box.cls
                    
                    y_max = b[3] - b[1]
                    x_max = b[2] - b[0]

                    if len(biggest) < 2:
                        biggest.append(b)
            
            self.currentBox = biggest
        #    print(self.currentBox)
            if keyboard.is_pressed('q'):
                lastKey = True
    
    def twoConesRunOnce(self):
        lastKey = False
        frame = self.display.grab(self.bounding_box)
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_BGRA2BGR)
        labels = self.model.predict(source = frame, conf = .50, save = False, verbose = False)

        biggest = []
        for r in labels: 
            boxes = r.boxes

            for box in boxes:
                b = box.xyxy[0] #(top-Left x) (top-Left Y) (Bottom-Right x) (Bottom-Right y))
                print(b)
                c = box.cls
                
                y_max = b[3] - b[1]
                x_max = b[2] - b[0]

                if len(biggest) < 2:
                    biggest.append(b)
        
        self.currentBox = biggest
        return biggest
        print(self.currentBox)


    
    def ReturnLabeledVideo(self):
        ret = True  # Initialize success flag
        while ret:
            print('running vision thread')
            frame = self.display.grab(self.bounding_box)

            if not ret:
                break  # Exit loop if frame capture fails (end of video)
            
            frame = cv2.cvtColor(np.array(frame), cv2.COLOR_BGRA2BGR)
            labels = self.model.predict(source = frame, conf = .40, save = False, verbose = False)

            biggest = [(-1,-1,-1,1), (-1, -1,-1,-1)]
            closeCones = [] 

            for r in labels: 
                ann = Annotator(frame)
                boxes = r.boxes

                for box in boxes:
                    b = box.xyxy[0] #(top-Left x) (top-Left Y) (Bottom-Right x) (Bottom-Right y))
                    print(b)
                    c = box.cls
                    
                    y_max = b[3] - b[1]
                    x_max = b[2] - b[0]

                    ann.box_label(b, self.model.names[int(c)])
                    if len(closeCones) < 2:
                        
                        closeCones.append(b)

            frame = ann.result()

            frame = cv2.resize(frame, (640,480))
            cv2.imshow("OutputWindow",frame)

            key = cv2.waitKey(1) & 0xFF  # Wait for a key press (1ms delay)
            if key == ord("q"):
                break  # Exit loop on 'q' press
            
            print("CONES ")
            print(closeCones)
    #        print(" ")
            self.currentBox = closeCones
        # Close all OpenCV windows
        cv2.destroyAllWindows()

        print("Video processing complete.")