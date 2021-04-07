from scripts.neat import neat_runner
from scripts.agent import Agent, TrainAgent

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import logging
from selenium.webdriver.remote.remote_connection import LOGGER

def setup():
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")

    return webdriver.Chrome(options=options)

import sys
import matplotlib.pyplot as plt

IS_TRAIN = sys.argv[1]

def run():
    def spawn_agent(genome):
        driver = setup()
        agent = TrainAgent(driver, genome) if IS_TRAIN else Agent(driver, genome)
        return agent.run()

    # Display results
    genome = neat_runner(spawn_agent)
    genome.draw()
    plt.show()

if __name__ == "__main__":
    run()
