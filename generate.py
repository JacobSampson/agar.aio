from scripts.agent import AgarioAgent, Agent, AggressiveAgent, DefensiveAgent, GreedyAgent, LocalAgent, AgarioAgent, NNAgent
from scripts.factories import DriverFactory, ServerFactory
from scripts.train import Train, TrainCont

import neat
import sys
import pickle

CHECKPOINT_FILE_NAME = sys.argv[1]
AGARIO_TRAIN_URL_FORMAT = "http://127.0.0.1:{}"

def run():
    print("Converting...")
    driver_factory = DriverFactory("http://127.0.0.1:{}", 3000, 1)
    neat = TrainCont(driver_factory, 1, CHECKPOINT_FILE_NAME)
    neat.main()

if __name__ == "__main__":
    run()
