from scripts.processing import process_inputs
from scripts.utils import get_driver_image
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
    SPEED_FACTOR = 20
    MAX_TIME_ALIVE = 30
    UPDATE_INTERVAL = 0.5
    THRESHOLD_SCORE = 100
    M = 61

    def __init__(self, driver, genome):
        # Sellenium
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)
        self.url = Agent.AGARIO_URL

        # Neural network
        self.genome = genome
        self.best_score = 0

        # Status
        self.creation_time = time.time()
        self.state = np.zeros(self.M)

    def setup(self):
        self.driver.get(self.AGARIO_URL)

        # Click start button
        play_button = self.wait.until(EC.element_to_be_clickable((By.ID, "play")))
        play_button.click()

    def close(self):
        self.driver.close()

    def move(self):
        pass

    def score(self):
        pass

    def is_dead(self):
        pass

    def is_done(self):
        return self.is_dead()

    def update(self):
        pass

    def get_state(self):
        return self.state

    def run(self):
        pass
        # self.setup()

        # # Main runner
        # while not(self.is_dead()) and (self.creation_time < self.MAX_SECS_ALIVE):
        #     self.update(self.get)
        #     time.sleep(self.UPDATE_INTERVAL)
        #     self.creation_time += self.UPDATE_INTERVAL

        # print(f"[log] Best score: {self.best_score}")

        # return self.best_score

class TrainAgent(Agent):
    AGARIO_URL = "http://192.168.99.100:3000/"

    def __init__(self, driver, genome, url):
        super().__init__(driver, genome)
        self.url = url

    def setup(self):
        self.driver.get(self.url)

        # Get canvas
        self.canvas = self.wait.until(EC.presence_of_element_located((By.ID, "cvs")))

        # Click start button
        play_button = self.wait.until(EC.element_to_be_clickable((By.ID, "startButton")))
        play_button.click()

        # Change settings to see mass
        chat_input = self.wait.until(EC.presence_of_element_located((By.ID, "chatInput")))
        chat_input.send_keys("-mass")
        chat_input.send_keys(Keys.ENTER)

    def move(self, x, y):
        size = self.canvas.size
        width, height= size["width"], size["height"]

        # Clamp outputs
        mouse_x = min(0, max(width, width / 2 + (x * self.SPEED_FACTOR)))
        mouse_y = min(0, max(height, height / 2 + (y * -1 * self.SPEED_FACTOR)))

        # Move mouse
        action = webdriver.ActionChains(self.driver)
        action.move_to_element_with_offset(self.canvas, mouse_x, mouse_y)
        action.perform()

    def score(self):
        try:
            return int(self.canvas.get_attribute('data-score'))
        except Exception as e:
            return 0

    def is_dead(self):
        start_menu = self.wait.until(EC.presence_of_element_located((By.ID, "startMenuWrapper")))
        return not (start_menu is None) and start_menu.value_of_css_property("max-height") == "1000px"

    def is_done(self):
        return (self.best_score > self.THRESHOLD_SCORE) or self.is_dead() or ((time.time() - self.creation_time) > self.MAX_TIME_ALIVE)

    def update(self, move):
        try:
            # Move
            x, y = move
            self.move(x, y)

            # Update state
            image = get_driver_image(self.driver, self.canvas)
            player, enemies, food = hough_circles(image)

            # print(f"Player [{self.best_score}]: {player}")
            # print(f"Enemies: {enemies}")
            # print(f"Food: {len(food)}")

            self.state = process_inputs(
                        player,
                        np.atleast_2d(np.array(enemies)),
                        np.atleast_2d(np.array(food)),
                        self.M)

            self.best_score = max(self.score(), self.best_score)

            return self.best_score
            # print(f"[log] Best score: {self.best_score}, x: {x}, y: {y}")
        except Exception as e:
            print(f"[log] Failed to update: {e}")
