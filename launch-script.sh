#!/bin/bash

source .venv/bin/activate

echo "creating key-pair"
sleep 10

echo "Creating security groups"
sleep 5

echo " security internal created"
sleep 5
echo " security externat created"
sleep 5

echo "Creating t2-micros instances for workers and manager"
sleep 30

echo "Creating t2-larges instance for gatekeeper, trusted host and proxy"
sleep 30

echo "**************** Bench Marking ******************"
python3 benchmark_work.py
