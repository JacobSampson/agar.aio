from scripts.train import Train, TrainCont
from scripts.agent import Agent, TrainAgent

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def setup():
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    options.add_argument("--log-level=3")

    return webdriver.Chrome(options=options)

import sys
import os
import signal
import subprocess
import time
from threading import Lock

IS_TRAIN = sys.argv[1]
NUM_GENERATIONS = int(sys.argv[2])
NUM_SERVERS = int(sys.argv[3])

CONT_TRAIN = len(sys.argv) == 5
CHECKPOINT_FILE_NAME = None if (not CONT_TRAIN) else sys.argv[4]

AGARIO_TRAIN_URL_FORMAT = "http://192.168.99.100:{}"
BASE_PORT = 3000

def run():
    pids = []
    try:
        # Start servers
        for i in range(0, NUM_SERVERS):
            curr_env = os.environ.copy()

            curr_env["SERVER_PORT"] = f'{BASE_PORT + i}'
            curr_env["COMPOSE_PROJECT_NAME"] = f'agario-{BASE_PORT + i}'

            # subprocess.Popen(["docker-compose", "-f", "servers/gulp/docker-compose.yaml", "up", "--build"], env=curr_env, stdout=subprocess.DEVNULL)
            subprocess.Popen(["docker-compose", "-f", "servers/gulp/docker-compose.yaml", "up"], env=curr_env, stdout=subprocess.DEVNULL)
            time.sleep(5)

        time.sleep(5 * NUM_SERVERS)

        print('[log] Starting agents')

        class AgentSpawner:
            def __init__(self, port, num_servers):
                self.base_port = port
                self.curr_port = port
                self.num_servers = num_servers

                # Multiprocessing
                self.mutex = Lock()

            # Generate agents
            def spawn(self, genome):
                # Thread-safe update port and create URL
                self.mutex.acquire()
                self.curr_port = self.curr_port + 1
                
                if self.curr_port > (self.base_port + self.num_servers - 1):
                    self.curr_port = self.base_port

                url = AGARIO_TRAIN_URL_FORMAT.format(self.curr_port)
                self.mutex.release()

                # Create driver and agent
                driver = setup()
                return TrainAgent(driver, genome, url=url) if IS_TRAIN else Agent(driver, genome)

        agent_spawner = AgentSpawner(BASE_PORT, NUM_SERVERS)

        neat = Train(agent_spawner, NUM_GENERATIONS) if (not CONT_TRAIN) else TrainCont(agent_spawner, NUM_GENERATIONS, CHECKPOINT_FILE_NAME)
        neat.main()
    finally:
        print('[log] Removing servers')
        for pid in pids:
            os.kill(pid, signal.CTRL_C_EVENT)

if __name__ == "__main__":
    run()
