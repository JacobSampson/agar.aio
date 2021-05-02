#!/bin/bash
files=$(ls checkpoints/history)
for file in $files; do
    if ! [[ ($file =~ .*.pkl) ]];
    then ./Python37/python generate.py ./checkpoints/history/$file ; mv ./checkpoints/winner.pkl ./checkpoints/history/$file.pkl ; echo "Next!"
    fi
done
