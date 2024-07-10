from gymnasium import Env
from ForzaGame import ForzaGame 
from typing import Optional
from gymnasium.spaces import Discrete, Box, Dict, Tuple
import numpy as np
import random
import time
import pyautogui

class GameEnv(Env):
    def __init__(self):
        # Actions we can take, down, stay, up
        
        self.GameController = ForzaGame()

        self.action_space = Discrete(6)
        # Twemperature array  x, y, detecting attempts to cheat the system 
        self.observation_space = Box(low= np.array([-1, 1, 0]), high = np.array([-1,1,8]), shape=(3,), dtype= np.int32)
        print("Shape " + str(self.observation_space))
        # Set start temp
        self.observation = np.array([0,0,0], dtype=np.float32)

        self.reward = 0

        self.GametimeAmount = 200

        self.firstrun = True
        # Set shower length
        self.game_length = self.GametimeAmount
    def releaseKeys(self):
        keys = ["w", "a", "d", "s"]
        for key in keys:
            pyautogui.keyUp(key) 
    def step(self, action):
        truncated = False
        terminated = False
        if action == 0:
            pyautogui.keyDown("w")
        elif action == 1:
            self.releaseKeys()
            pyautogui.keyDown("w")
            pyautogui.keyDown("a")
        elif action == 2:
            self.releaseKeys()
            pyautogui.keyDown("w")
            pyautogui.keyDown("d")
        elif action == 3:
            self.releaseKeys()
            pyautogui.keyDown("s")
        elif action == 4:
            self.releaseKeys()
        elif action == 5:
            pass

        if self.GameController.checkGameUpdate():                   #If the game finishes as true
            self.reward = self.game_length / self.GametimeAmount * 100
            terminated = True
        
        self.reward += self.GameController.points
        self.observation[0] = self.GameController.distanceX
        self.observation[1] = self.GameController.distanceY
        self.observation[2] = self.GameController.falseAlerts
        # Reduce shower length by 1 second
        self.game_length -= 1 
        
        if self.game_length <= 0: 
            self.reward - 10000
            terminated = True

        print(self.game_length)
        # Apply temperature noise
        #self.state += random.randint(-1,1)
        # Set placeholder for info
        info = {}
        
        # Return step information
        return self.observation, self.reward, terminated, truncated, info

    def render(self):
        # Implement viz
        pass
    def loseInputs(self):
            print("lose inputs running")
            pyautogui.press('esc')
            time.sleep(1)
            pyautogui.press('right')
            pyautogui.press('down')

    #def reset(self, seed)
    def reset(self,
        *,
        seed: Optional[int] = None,
        return_info: bool = False,
        options: Optional[dict] = None,
    ):
        # Reset shower temperature
        print("Running reset script" + str(self.game_length))
        self.reward = 0
        self.releaseKeys()
        if self.game_length == 0 or self.GameController.falseAlerts == 8:     # Time ran out!
            self.loseInputs()
            pyautogui.press('enter')
            time.sleep(.5)
            pyautogui.press('enter')
            time.sleep(4)
            pyautogui.press('enter')
    
        elif self.firstrun:
            self.firstrun = False 

        else:    
            self.loseInputs()   #False positives are relatively commmen, so we do the following to ensure the reamiaing games can finish as expected
            print("Running Winning script")
            time.sleep(4)
    #        pyautogui.press('x')  The following steps will be done by the game itself
    #        pyautogui.press('enter')
            print("pressin x win")
            pyautogui.press('x')
            print("enter 2")
            time.sleep(1.5)
            pyautogui.press('enter')
            print('Enter 3')
            time.sleep(5.8)
            pyautogui.press('enter')
        time.sleep(3)               # Allow game to load after rest
        
        self.observation = np.array([0,0,0], dtype=np.float32)


        self.GameController.falseAlerts = 0 
        # Reset shower time
        self.game_length = self.GametimeAmount 
        self.GameController.consistenCheckFails = 0
        return (self.observation , {})
    
pyautogui.getWindowsWithTitle("Forza Horizon 5")[0].activate()
env = GameEnv()
#env = gym.make("CartPole-v1")

env.observation_space.sample()

episodes = 10
"""for episode in range(1, episodes+1):
    state = env.reset()
    done = False
    score = 0 
#    
#    
    while not done:
        #env.render()
        action = env.action_space.sample()
        n_state, reward, done, info = env.step(action)
        score+=reward
        print(score)
    print('Episode:{} Score:{}'.format(episode, score))  """

###### Training the model
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Flatten
from tensorflow.keras.optimizers import Adam  

#states = [len(env.observation_space)]
actions = env.action_space.n

print("Actions: " + str(actions))

def build_model(states, actions):
    model = Sequential()    
    model.add(Dense(24, activation='relu', input_shape=states))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(actions, activation='linear'))
    return model

#model = build_model(states, actions)


#model.summary()


from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.env_checker import check_env


env = DummyVecEnv([lambda: GameEnv()])
env.reset()
#check_env(env)

model = DQN('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=10000)

model.save("dqn_forza_model")