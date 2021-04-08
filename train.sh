#!/bin/bash

# USAGE: <IS_TRAIN> <NUM_GENERATIONS> <NUM_SERVERS> <CONT_TRAIN> <CHECKPOINT_FILE_NAME>
# python main.py 1 500 20 ./checkpoints/checkpoint-4
# python main.py 1 500 20
python main.py 1 4 2

# echo "y" | docker container prune
