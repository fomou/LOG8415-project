#!/bin/bash

sudo rm Project-key-pair.pem 2 > /dev/null
cp ~/.aws/credentials credentials
export VENV=.venv

if [ ! -d "$VENV" ]; then
  virtualenv .venv -p python3
fi

source .venv/bin/activate

pip install -r requirements.txt
source .venv/bin/activate

python3 main.py
sleep 30

echo "**************** Bench Marking ******************"
python3 benchmark_work.py
