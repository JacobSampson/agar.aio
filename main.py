from scripts.agent import Agent, AggressiveAgent, DefensiveAgent, GreedyAgent, LocalAgent
from scripts.factories import DriverFactory, ServerFactory
from scripts.train import Train, TrainCont

import sys
import os
import signal
import subprocess
import time
from threading import Lock, Thread

# Arguments
# TODO: Convert to named arguments

IS_TRAIN = sys.argv[1]
NUM_GENERATIONS = int(sys.argv[2])
NUM_SERVERS = int(sys.argv[3])

CONT_TRAIN = len(sys.argv) == 5
CHECKPOINT_FILE_NAME = None if (not CONT_TRAIN) else sys.argv[4]

# Constants

AGARIO_TRAIN_URL_FORMAT = "http://192.168.99.100:{}"
AGARIO_TEST_URL = "http://192.168.99.100:3000"
BASE_PORT = 3000

def train():
    pids = []
    try:
        # Start servers
        for i in range(0, NUM_SERVERS):
            pids.append(ServerFactory.create(BASE_PORT + i))
            time.sleep(5)

        time.sleep(20 * NUM_SERVERS)

        print('[log] Starting')

        driver_factory = DriverFactory(AGARIO_TRAIN_URL_FORMAT, BASE_PORT, NUM_SERVERS)
        neat = Train(driver_factory, NUM_GENERATIONS) if (not CONT_TRAIN) else TrainCont(driver_factory, NUM_GENERATIONS, CHECKPOINT_FILE_NAME)
        neat.main()
    finally:
        print('[log] Removing servers')
        for pid in pids:
            os.kill(pid, signal.CTRL_C_EVENT)

def test():
    # try:
    # pid = ServerFactory.create(BASE_PORT)
    # time.sleep(20)

    print('[log] Starting')

    agents = [
        lambda driver, url: AggressiveAgent(driver, url),
        lambda driver, url: GreedyAgent(driver, url),
        lambda driver, url: DefensiveAgent(driver, url)
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

        while True: pass
    finally:
        for thread in threads:
            thread.join()

    # finally:

    #     print('[log] Removing server')
    # os.kill(pid, signal.CTRL_C_EVENT)    

if __name__ == "__main__":
    # train()
    test()
