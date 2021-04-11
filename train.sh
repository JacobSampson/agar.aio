#!/bin/bash

# USAGE: <IS_TRAIN> <NUM_GENERATIONS> <NUM_SERVERS> <CONT_TRAIN> <CHECKPOINT_FILE_NAME>
# python main.py 1 500 3 ./checkpoints/checkpoint-72
python main.py 1 500 7

# echo "y" | docker container prune
