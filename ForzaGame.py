from Vision import Vision
import time
import threading
import keyboard
import pyautogui


class ForzaGame():
    def __init__(self):
        print("Please navigate to the EventLab Course Creater before we began")
        self.centerTensor = [802, 600, 787, 820]  # will use Y to See when the cones are behind
        self.vision = Vision()
        
        self.points = 0
        self.falseAlerts = 0

        self.distanceY = 0
        self.distanceX = 0

        self.stop_timer = threading.Event()
        self.timerFinished = threading.Event()
        self.timeOut = threading.Event()

#        endTime = threading.Thread(target=self.timer, args=[60])  #TIME FOR AUTO END

#        endTime.start()
   #      MainGame.start()
    #    self.MainGame()
        #self.vision.twoClosestCones()
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
        while runs < 15:
            print("hits:" + str(hits))
            print("Runs:" + str(runs))
            print( "NC" + str(self.vision.twoConesRunOnce()))
            if len(self.vision.twoConesRunOnce()) > 0:
                hits += 1
            if hits == 1:
                print("False Alert")
                self.points -= 10
                self.falseAlerts += 1
                return False
            runs += 1
        return True                 # Program decieded the amount of cones = 0
        
    def checkInBetween(self, currentBox):
        print("inbetween")
        if len(currentBox) == 2:
            values = []
            for index, box in enumerate(currentBox):
                values.append((box[0].item()/1920) - (self.centerTensor[0]/1920))
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
            return True
        else:
            return False
    
    def releaseArrowKey(self):
        options = ["top", "left", "right", "up"]
        for ops in options:
            pyautogui.keyUp(ops)

    
    def lookAroundForCones(self):
        print("checking for cones")
        pyautogui.keyDown("top")
        pyautogui.keyDown("left")
        if self.CheckConeInScene():
            self.releaseArrowKey()
            print("cones fount stage 1")
            return True
        pyautogui.keyUp("top")
        pyautogui.keyDown("down")
        time.sleep(.15)
        if self.CheckConeInScene():
            print("cones fount stage 1")
            self.releaseArrowKey()
            return True
        pyautogui.keyUp("left")
        time.sleep(.15)
        if self.CheckConeInScene():
            print("cones fount stage 1")
            self.releaseArrowKey()
            return True
        pyautogui.keyDown("right")
        time.sleep(.15)        
        if  self.CheckConeInScene():
            print("cones fount stage 1")
            self.releaseArrowKey()
            return True
        pyautogui.keyUp("down")    
        time.sleep(.15)
        if  self.CheckConeInScene():
            self.releaseArrowKey()
            return True
        pyautogui.keyUp("right")
        
        return False
    
    def releaseControlKeys(self):
        options = ["s", "a", "d", "w"]
        for ops in options:
            pyautogui.keyUp(ops)

    def ResetCarPositionCheckCones(self):
        self.releaseControlKeys()
        pyautogui.press('esc')
        time.sleep(.8)
        pyautogui.press('x')
        time.sleep(.4)
        pyautogui.press('enter')
        time.sleep(2.5)

        if self.checkNoCones():
            return True                 #Found no cones after rerunning
        else:
            return False



    def checkBehindHood(self, currentBox):
        if len(currentBox) == 2:
            for box in currentBox:
                self.distanceY = (box[1].item()/1080) - (self.centerTensor[1] /1080) 
                if box[1].item() < self.centerTensor[1]:
                    print("Behind")
                    self.points += 10
                    return True         # The Detected Cones are behind
                else: 
                    self.points -= 2
                    return False

        return False

    def checkGameUpdate(self): 
        currentBox = self.vision.twoConesRunOnce() 
        self.points = 0 
        print(currentBox)
        print(str(self.falseAlerts) + " False")
        if self.checkBehindHood(currentBox) and self.checkInBetween(currentBox):
            self.points += 10
        elif len(self.vision.currentBox) == 0:
            if(self.checkNoCones()):
                if self.ResetCarPositionCheckCones():
                    print("You win! " + str(self.points) + " points")
                    return True
                else:
                    print("we ended up finding cones after reseting")
                    self.points -= 15
        elif self.falseAlerts == 8:
            print("You Lose! " + str(self.points) + " points")
            return True
        if self.checkBehindHood(currentBox) or self.checkInBetween(currentBox):
            self.falseAlerts == 0

            

