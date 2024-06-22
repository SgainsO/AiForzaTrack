from gym import Env
from ForzaGame import ForzaGame 
from gym.spaces import Discrete, Box, Dict, Tuple
import numpy as np
import random
import time
import pyautogui
import gym

class GameEnv(Env):
    def __init__(self):
        # Actions we can take, down, stay, up
        
        self.GameController = ForzaGame()

        self.action_space = Discrete(6)
        # Twemperature array  x, y, detecting attempts to cheat the system 
        self.observation_space = Tuple((Box(-1,1, shape=(1,)), Box(-1,1, shape=(1,)), Discrete(8)), seed= 42)
        print("Shape " + str(self.observation_space))
        # Set start temp
        self.state = np.array([0,0,0], dtype=np.float32)

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
        done = False
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
            done = True
        
        self.reward += self.GameController.points
        self.state[0] = self.GameController.distanceX
        self.state[1] = self.GameController.distanceY
        self.state[2] = self.GameController.falseAlerts
        # Reduce shower length by 1 second
        self.game_length -= 1 
        
        if self.game_length <= 0: 
            self.reward - 10000
            done = True

        print(self.game_length)
        # Apply temperature noise
        #self.state += random.randint(-1,1)
        # Set placeholder for info
        info = {}
        
        # Return step information
        return self.state, self.reward, done, info

    def render(self):
        # Implement viz
        pass
    def loseInputs(self):
            print("lose inputs running")
            pyautogui.press('esc')
            time.sleep(1)
            pyautogui.press('right')
            pyautogui.press('down')


    def reset(self):
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
        
        self.state = np.array([0,0,0], dtype=np.float32)


        self.GameController.falseAlerts = 0 
        # Reset shower time
        self.game_length = self.GametimeAmount 
        self.GameController.consistenCheckFails = 0
        return self.state
    
#pyautogui.getWindowsWithTitle("Forza Horizon 5")[0].activate()
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

states = [len(env.observation_space)]
actions = env.action_space.n

print("Actions: " + str(actions))

def build_model(states, actions):
    model = Sequential()    
    model.add(Dense(24, activation='relu', input_shape=states))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(actions, activation='linear'))
    return model

model = build_model(states, actions)


model.summary()
from rl.agents import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

def build_agent(model, actions):
    policy = BoltzmannQPolicy()
    memory = SequentialMemory(limit=50000, window_length=1)
    dqn = DQNAgent(model=model, memory=memory, policy=policy, 
                  nb_actions=actions, nb_steps_warmup=10, target_model_update=1e-2)
    return dqn


dqn = build_agent(model, actions)

dqn.compile(Adam(learning_rate = 0.001), metrics= ["mae"])

dqn.fit(env, nb_steps=10000, visualize=False, verbose=1)


scores = dqn.test(env, nb_episodes=50, visualize=False)
print(np.mean(scores.history['episode_reward']))

dqn.save_weights('forza_model.h5f', overwrite=True)