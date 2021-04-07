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
    MAX_SECS_ALIVE = 30

    def __init__(self, driver, genome):
        # Sellenium
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

        # Neural network
        self.genome = genome
        self.best_score = 0

        self.time_alive = 0

    def setup(self):
        self.driver.get(self.AGARIO_URL)

        # Click start button
        play_button = self.wait.until(EC.element_to_be_clickable((By.ID, "play")))
        play_button.click()

    def move(self):
        pass

    def score(self):
        pass

    def get_direction(player, enemies, food):
        pass

    def is_dead(self):
        pass

    def update(self):
        pass

    def run(self):
        self.setup()

        UPDATE_INTERVAL = 0.5

        # Main runner
        while not(self.is_dead()) and (self.time_alive < self.MAX_SECS_ALIVE):
            self.update()
            time.sleep(UPDATE_INTERVAL)
            self.time_alive += UPDATE_INTERVAL

        print(f"[log] Best score: {self.best_score}")

        return self.best_score

class TrainAgent(Agent):
    AGARIO_URL = "http://192.168.99.100:3000/"

    def setup(self):
        self.driver.get(self.AGARIO_URL)

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

        # Move mouse
        action = webdriver.ActionChains(self.driver)
        action.move_to_element_with_offset(self.canvas, width / 2 + (x * self.SPEED_FACTOR), height / 2 + (y * -1 * self.SPEED_FACTOR))
        action.perform()

    def score(self, player):
        if (len(player) < 3):
            return float("-inf")

        return player[2]

    def get_direction(self, player, enemies, food):
        M = 20

        inputs = process_inputs(
                    np.array(player),
                    np.atleast_2d(np.array(enemies)),
                    np.atleast_2d(np.array(food)),
                    M)
        N = len(inputs[0])

        return self.genome(inputs)

        return [0.5, 0.5]
        # return self.genome(player, enemies, food)

    def is_dead(self):
        start_menu = self.wait.until(EC.presence_of_element_located((By.ID, "startMenuWrapper")))
        return not (start_menu is None) and start_menu.value_of_css_property("max-height") == "1000px"

    def update(self):
        # Get current field
        # try:
            image = get_driver_image(self.driver, self.canvas)
            player, enemies, food = hough_circles(image)

            # print(f"Player [{self.best_score}]: {player}")
            # print(f"Enemies: {enemies}")
            # print(f"Food: {len(food)}")

            self.best_score = max(self.score(player), self.best_score)
            x, y = self.get_direction(player, enemies, food)
            self.move(x, y)
            # print(f"[log] Best score: {self.best_score}, x: {x}, y: {y}")
        # except Exception as e:
        #     print(f"[log] Failed to move: {e}")
