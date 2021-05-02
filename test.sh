#!/bin/bash

files=$(ls checkpoints/history)
for file in $files; do
    if [[ ($file =~ .*.pkl) ]]; 
    then echo $file ; WINNER_FILE_NAME=$file ./Python37/python main.py 0 0 0 ./checkpoints/history/$file
    fi
done
