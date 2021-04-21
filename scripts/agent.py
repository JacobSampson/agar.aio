from scripts.processing import process_inputs, reduce_state
from scripts.utils import get_driver_image, get_driver_screenshot
from scripts.image import hough_circles
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

import numpy as np

import random
import time

class Agent:
    AGARIO_URL = "https://agar.io"
    SPEED_FACTOR = 1
    MAX_TIME_ALIVE = 30
    UPDATE_INTERVAL = 0.5
    THRESHOLD_SCORE = 200

    M = 6
    SPLIT = 0.6

    def __init__(self, driver, url=AGARIO_URL):
        # Sellenium
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)
        self.url = url
        self.canvas = None

        # Neural network
        self.curr_score = 0

        # Status
        self.creation_time = time.time()
        self.state = np.zeros(self.M)

    def setup(self):
        self.driver.get(self.url)

    def close(self):
        self.driver.close()
        self.driver = None

    def move(self, x, y):
        size = self.canvas.size
        width, height = size["width"], size["height"]

        # Clamp outputs
        BUFFER = 10
        mouse_x = max(BUFFER, min(width - BUFFER, width / 2. + (x * self.SPEED_FACTOR)))
        mouse_y = max(BUFFER, min(height - BUFFER, height / 2. + (y * -1 * self.SPEED_FACTOR)))

        # Move mouse
        action = webdriver.ActionChains(self.driver)
        action.move_to_element_with_offset(self.canvas, mouse_x, mouse_y)
        action.perform()

    def get_image(self):
        return get_driver_image(self.driver, self.canvas)

    def score(self):
        raise NotImplementedError

    def is_dead(self):
        raise NotImplementedError

    def is_done(self):
        raise NotImplementedError

    def update(self):
        self.sleep()

    def get_state(self):
        return self.state

    def get_state_components(self):
        return reduce_state(self.state, self.M, self.SPLIT)

    def sleep(self):
        time.sleep(self.UPDATE_INTERVAL)

    def get_move(self):
        return [0,0]

    def run(self):
        self.setup()

        # Main runner
        while not(self.is_done()):
            self.update()

        print(f"[log] Final score: {self.curr_score}")

        return self.curr_score

class LocalAgent(Agent):
    AGARIO_URL = "http://127.0.0.1:3000/"
    CLASS_NAME = "LOCAL"

    def setup(self):
        super().setup()
        print(f'[log] Starting {self.CLASS_NAME}')

        # Get canvas
        self.canvas = self.wait.until(EC.presence_of_element_located((By.ID, "cvs")))

        # Click start button
        play_button = self.wait.until(EC.element_to_be_clickable((By.ID, "startButton")))
        play_button.click()

        # Change settings to see mass
        # chat_input = self.wait.until(EC.presence_of_element_located((By.ID, "chatInput")))
        # chat_input.send_keys("-mass")
        # chat_input.send_keys(Keys.ENTER)

    def score(self):
        try:
            return int(self.canvas.get_attribute('data-score'))
        except Exception:
            return 0

    def is_dead(self):
        start_menu = self.wait.until(EC.presence_of_element_located((By.ID, "startMenuWrapper")))
        return not (start_menu is None) and start_menu.value_of_css_property("max-height") == "1000px"

    def is_done(self):
        is_done = (self.curr_score > self.THRESHOLD_SCORE) or self.is_dead() or ((time.time() - self.creation_time) > self.MAX_TIME_ALIVE)
        return is_done

    def update(self):
        try:
            # Update state
            image = self.get_image()
            player, enemies, food = hough_circles(image)

            self.state = process_inputs(
                            player,
                            np.atleast_2d(np.array(enemies)),
                            np.atleast_2d(np.array(food)),
                            self.M,
                            self.SPLIT)

            self.curr_score = self.score()

            x, y = self.get_move()
            self.move(x, y)

            return self.curr_score

        except Exception as e:
            print(f"[log] Failed to update: {e}")

class NNAgent(LocalAgent):
    # MAX_TIME_ALIVE = float("inf")
    CLASS_NAME = "NN"

    def __init__(self, driver, url, net):
        super().__init__(driver, url)
        self.net = net

    def get_move(self):
        move = self.net.activate(self.get_state())
        return move

class GreedyAgent(LocalAgent):
    # MAX_TIME_ALIVE = float("inf")
    CLASS_NAME = "GREEDY"

    def get_move(self):
        _, _, food = self.get_state_components()

        # Closest food
        return food[0]

class AggressiveAgent(LocalAgent):
    # MAX_TIME_ALIVE = float("inf")
    CLASS_NAME = "AGGRESSIVE"

    def get_move(self):
        player_radius, enemies, food = self.get_state_components()

        for enemy in enemies:
            if not ((enemy[0] == 0) and (enemy[2] == 0)) and player_radius > enemy[2]:
                return enemy[0:2]

        # Closest food
        return food[0]

class DefensiveAgent(LocalAgent):
    # MAX_TIME_ALIVE = float("inf")
    CLOSEST_AGENT = 50
    CLASS_NAME = "DEFENSIVE"

    def get_move(self):
        _, enemies, food = self.get_state_components()

        if len(enemies) > 0:
            closest_enemy = enemies[0]
            dist_closest_enemy = No(((closest_enemy[0]) ** 2) + ((closest_enemy[1]) ** 2)) ** (0.5)

            # Run from closest enemy, if within distance threshold
            if dist_closest_enemy < DefensiveAgent.CLOSEST_AGENT:
                return [-closest_enemy[0], -closest_enemy[1]]

        # Closest food
        return food[0]

class AgarioAgent(NNAgent):
    MAX_TIME_ALIVE = float("inf")
    CLASS_NAME = "AGARIO"

    def setup(self):
        Agent.setup(self)

        # Get canvas
        self.canvas = self.wait.until(EC.presence_of_element_located((By.ID, "canvas")))

        # Click start button
        play_button = self.wait.until(EC.element_to_be_clickable((By.ID, "play")))
        play_button.click()

        # Wait for CAPTCHA
        # time.sleep(120)
        # WebDriverWait(self.driver, 60).until(EC.invisibility_of_element_located((By.ID, "rc-anchor-container")))

    def is_done(self):
        # Keeps agent going until death
        return self.is_dead()

    def get_image(self):
        return get_driver_screenshot(self.driver, self.canvas)
