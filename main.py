#! C:/agar.aio-master/Python37

from scripts.agent import AgarioAgent, Agent, AggressiveAgent, DefensiveAgent, GreedyAgent, LocalAgent, AgarioAgent, NNAgent
from scripts.factories import DriverFactory, ServerFactory
from scripts.train import Train, TrainCont

import sys
import pickle
import os
import signal
import subprocess
import time
from threading import Lock, Thread

import neat

# Arguments
# TODO: Convert to named arguments

IS_TRAIN = sys.argv[1]
NUM_GENERATIONS = int(sys.argv[2])
NUM_SERVERS = int(sys.argv[3])

CONT_TRAIN = len(sys.argv) == 5
CHECKPOINT_FILE_NAME = None if (not CONT_TRAIN) else sys.argv[4]

WINNER_FILE_NAME = "./checkpoints/4.10.2021/winner.pkl"
CONFIG_FILE_NAME = "./scripts/config"

# Constants

AGARIO_TRAIN_URL_FORMAT = "http://127.0.0.1:{}"
AGARIO_TEST_URL = "http://127.0.0.1:3000"
# AGARIO_TEST_URL = "https://agar.io"
BASE_PORT = 3000

def train():
    pids = []
    try:
        # Start servers
        for i in range(0, NUM_SERVERS):
            pids.append(ServerFactory.create(BASE_PORT + i))
            time.sleep(5)

        time.sleep(10 * NUM_SERVERS)

        print('[log] Starting')

        driver_factory = DriverFactory(AGARIO_TRAIN_URL_FORMAT, BASE_PORT, NUM_SERVERS)
        neat = Train(driver_factory, NUM_GENERATIONS) if (not CONT_TRAIN) else TrainCont(driver_factory, NUM_GENERATIONS, CHECKPOINT_FILE_NAME)
        neat.main()
    except Exception as e:
        print(e)
    finally:
        print('[log] Removing servers')
        for pid in pids:
            os.kill(pid, signal.CTRL_C_EVENT)

def test():
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        CONFIG_FILE_NAME)
    genome = pickle.load(open(WINNER_FILE_NAME, "rb"))
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    agents = [
        lambda driver, url: NNAgent(driver, url, net),

        # lambda driver, url: AgarioAgent(driver, url),
        # lambda driver, url: AggressiveAgent(driver, url),
        # lambda driver, url: GreedyAgent(driver, url),
        # lambda driver, url: DefensiveAgent(driver, url)
    ]
    driver_factory = DriverFactory(AGARIO_TEST_URL)

    threads = []
    try:
        for agent_spawner in agents:
            driver, url = driver_factory.create()
            agent = agent_spawner(driver, url)

            thread = Thread(target=agent.run)
            threads.append(thread)
            thread.start()
    finally:
        for thread in threads:
            thread.join()

if __name__ == "__main__":
    # train()
    test()
