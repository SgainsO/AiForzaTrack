from Vision import Vision
import time
import threading
import keyboard
import pyautogui


class ForzaGame():
    def __init__(self):
        pyautogui.getWindowsWithTitle("Forza Horizon 5")[0].activate()
        print("Please navigate to the EventLab Course Creater before we began")
        self.centerTensor = [802, 600, 787, 820]  # will use Y to See when the cones are behind
        self.vision = Vision()
        self.points = 0
        self.falseAlerts = 0

        self.stop_timer = threading.Event()
        self.timerFinished = threading.Event()
        self.timeOut = threading.Event()

#        endTime = threading.Thread(target=self.timer, args=[60])  #TIME FOR AUTO END
        mainControls = threading.Thread(target=self.MainGame)

        mainControls.start()
#        endTime.start()
        #MainGame.start()
    #    self.MainGame()
        self.vision.twoClosestCones()
        print("Vision Stopped")

    def timer(self, duration):
        print(f"Timer started for {duration} seconds.")
        start_time = time.time()
        while time.time() - start_time < duration:
            if self.stop_timer.is_set():
                print("Timer stopped early.")
                return
            self.vision.twoConesRunOnce()
            time.sleep(0.1)  # Sleep for a short duration to prevent busy-waiting
        print("Timer ended.")
        self.timerFinished.set()

    def Win(self):
        self.points += 19
        pyautogui.press('esc')
        time.sleep(5)
        return True
    
    def Loss(self):
        self.points -= 20
        pyautogui.press('esc')
        pyautogui.getWindowsWithTitle("ForzaGame.py - ForzaControl - Visual Studio Code")[0].activate()
        pyautogui.press('q')
        start_time = time.time()

        while time.time() - start_time < 1:
            pyautogui.press('q')  # Hold the 'q' key

    def StartNew(self):
        pyautogui.press('right')
        pyautogui.press('down')
        pyautogui.press('enter')

    def MainGame(self):
        pyautogui.press('esc')
        time.sleep(3)
        running = True
        while running:
            print(self.vision.currentBox)
            self.checkGameUpdate()


    def checkNoCones(self):
        print("There may not be any cones")
        runs = 0
        hits = 0
        while runs < 1000:
            if len(self.vision.currentBox) == 0:
                hits += 1
            if hits == 750:
                self.falseAlerts += 1
                return False
            runs += 1
        return True
        
    def checkInBetween(self):
        if len(self.vision.currentBox) == 2:
            values = []
            for index, box in enumerate(self.vision.currentBox):
                values.append(box[0].item() - self.centerTensor[0])
                print("Values "+ str(values))
            print(values[0] * values[1])
            if values[0] * values[1] > 0:                       #It is not inbetween 
                self.points -= 5
                return False
            else:
    #            print("In between!!")
                return True
            
    def CheckConeInScene(self):
        if(len(self.vision.currentBox) != 0):
            return False
        else:
            return True
    

    
    def lookAroundForCones(self):
        print("You may have won: looking now")
        pyautogui.keyDown("top")
        pyautogui.keyDown("left")
        if not self.CheckConeInScene():
            return True
        pyautogui.keyUp("top")
        pyautogui.keyDown("down")
        if not self.CheckConeInScene():
            return True
        pyautogui.keyUp("left")
        if not self.CheckConeInScene():
            return True
        pyautogui.keyDown("right")
        if not self.CheckConeInScene():
            return True
        pyautogui.keyUp("down")    
        if not self.CheckConeInScene():
            return True
        pyautogui.keyUp("right")

    def checkBehindHood(self):
        if len(self.vision.currentBox) == 2:
            for box in self.vision.currentBox:
                if box[1].item() < self.centerTensor[1]:
                    print("Behind")
                    return True         # The Detected Cones are behind
                else: 
                    return False

    def checkGameUpdate(self): 
        if self.checkBehindHood() and self.checkInBetween():
            self.points += 10
        elif len(self.vision.currentBox) == 0:
            if(self.checkNoCones):
                if not self.lookAroundForCones():
                    self.Win()
                    print("You win! " + str(self.points) + " points")
                else:
                    self.points -= 15
        elif self.falseAlerts == 5:
            print("You Lose! " + str(self.points) + " points")
            self.Loss()
            

#Vision().ReturnLabeledVideo()
ForzaGame()