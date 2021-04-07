#!/bin/bash

git clone https://github.com/goktug97/NEAT
cd NEAT
python setup.py install --user

git clone https://github.com/EndingCredits/Object-Based-RL.git
cd Object-Based-RL
pip install -r requirements.txt
