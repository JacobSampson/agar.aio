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
import numpy as np
import pandas as pd

# Arguments
# TODO: Convert to named arguments

# IS_TRAIN = sys.argv[1]
IS_TRAIN = False
NUM_GENERATIONS = int(sys.argv[2])
NUM_SERVERS = int(sys.argv[3])

CONT_TRAIN = len(sys.argv) == 5
CHECKPOINT_FILE_NAME = None if (not CONT_TRAIN) else sys.argv[4]

WINNER_FILE_NAME = "./checkpoints/4.20.2021/winner.pkl"
# WINNER_FILE_NAME = os.environ["WINNER_FILE_NAME"]
CONFIG_FILE_NAME = "./scripts/config"
NUM_RUNS = 50

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

def basic():
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        CONFIG_FILE_NAME)
    genome = pickle.load(open(WINNER_FILE_NAME, "rb"))
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    try:
        agents = [
            lambda driver, url: NNAgent(driver, url, net),

            # lambda driver, url: AggressiveAgent(driver, url),
            # lambda driver, url: G
            # reedyAgent(driver, url),
            # lambda driver, url: DefensiveAgent(driver, url)

            # lambda driver, url: AgarioAgent(driver, url, net),
        ]

        driver, url = DriverFactory(AGARIO_TEST_URL).create()
        agent = NNAgent(driver, AGARIO_TEST_URL, net)
        agent.run()
    except Exception as e:
        print(e)

    sys.exit()

def test():
    # pid = ServerFactory.create(BASE_PORT)
    time.sleep(15)

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        CONFIG_FILE_NAME)
    genome = pickle.load(open("./checkpoints/history/%s" % WINNER_FILE_NAME, "rb"))
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    scores = pd.DataFrame(columns=["checkpoint", "run", "score", "player"])
    try:
        for num_run in range(NUM_RUNS):
            print('[log] Run %d' % num_run)
            agents = [
                lambda driver, url: NNAgent(driver, url, net),

                # lambda driver, url: AggressiveAgent(driver, url),
                # lambda driver, url: GreedyAgent(driver, url),
                # lambda driver, url: DefensiveAgent(driver, url)

                # lambda driver, url: AgarioAgent(driver, url, net),
            ]
            driver_factory = DriverFactory(AGARIO_TEST_URL)

            threads = []
            for (index, agent_spawner) in enumerate(agents):
                driver, url = driver_factory.create()
                agent = agent_spawner(driver, url)

                def score_agent(agent):
                    def score_agent():
                        score = agent.run()

                        # Add score to record
                        rows, _ = scores.shape
                        scores.loc[rows] = [WINNER_FILE_NAME.split('.')[0], num_run, score, agent.CLASS_NAME]

                    return score_agent

                thread = Thread(target=score_agent(agent))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            time.sleep(15)
    except Exception as e:
        print(e)
    finally:
        scores.to_csv('checkpoints/scores.csv', index=False, mode='a', header=False)
        # os.kill(pid, signal.CTRL_C_EVENT)

    sys.exit()

if __name__ == "__main__":
    if IS_TRAIN:
        print('Training...')
        train()
    else:
        print('Testing...')
        # test()
        basic()
