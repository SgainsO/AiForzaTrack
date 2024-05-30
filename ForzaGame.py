from Vision import Vision
import time
import threading
import pyautogui


Vision().ReturnLabeledVideo()

class ForzaGame():
    def __init__(self):
        pyautogui.getWindowsWithTitle("Forza Horizon 5")[0].activate()
        print("Please navigate to the EventLab Course Creater before we began")
        self.centerTensor = [802, 640, 787, 820]  # will use Y to See when the cones are behind
        self.vision = Vision()
        self.stop_timmer = threading.event()
        self.timerFinished = threading.event()
        self.timeOut = threading.Event
        self.points = 0

        visionThread = threading.Thread(target= self.vision.twoClosestCones)
        endTime = threading.Thread(target=self.timer, args=(15, ))
        endTime.start()
        visionThread.start()

    def timer(self, duration):
        print(f"Timer started for {duration} seconds.")
        start_time = time.time()
        while time.time() - start_time < duration:
            if self.stop_timer.is_set():
                print("Timer stopped early.")
                return
            time.sleep(0.1)  # Sleep for a short duration to prevent busy-waiting
        print("Timer ended.")
        self.timerFinished.set()

    def Win(self):
        self.points += 19
        pyautogui.press('esc')
        return True
    
    def Loss(self):
        self.points -= 20
        pyautogui.press('esc')

    def StartNew(self):
        pyautogui.press('right')
        pyautogui.press('down')
        pyautogui.press('enter')

    def MainGame(self):
        running = True
        while running:
            pressed_key = pyautogui.getKey()
            if pressed_key in ["w", "a", "s", "d", "q", "e"]:
                pyautogui.press(pressed_key)
    

    def checkNoConesForFive(self):
        self.stop_timmer.clear()
        noCones = True
        timerThread = threading.Thread(target= self.timer, args = (5))
        timerThread.start()
        while not self.timerFinished.is_set():
            if len(self.vision.currentBox) > 0:
                self.stop_timmer.set()
                noCones = False
            self.points -= 1
        self.timerFinished.clear()
        return noCones
        
    def checkInBetween(self):
        if len(self.vision.currentBox) == 2:
            values = []
            for index, box in enumerate(self.vision.currentBox):
                values[index] = box[0] - self.centerTensor[0]
            if values[0] * values[1] > 0:                       #It is not inbetween 
                return False
            else:
                self.points -= 5
                return True
    def lookAroundForCones(self):
        pass
    def checkBehindHood(self):
        if len(self.vision.currentBox) == 2:
            for box in self.vision.currentBox:
                if box[0] < self.centerTensor[0]:
                    return True         # The Detected Cones are behind
                else: 
                    return False

    def checkGameUpdate(self): 
        if self.checkBehindHood() and self.checkInBetween():
            self.points += 10
        elif len(self.vision.currentBox) == 0:
            if(self.checkNoConesForFive):
                if not self.lookAroundForCones():
                    self.Win()
                else:
                    self.points -= 15
        elif self.timeOut.is_set():
            self.Loss()
            
        


            



   

                