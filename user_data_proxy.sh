
# Install MySQL Server and Sysbench
sudo apt-get update
sudo apt-get install mysql-server sysbench python3-venv -y

cd /home/ubuntu
git clone https://github.com/fomou/LOG8415-project.git

cd LOG8415-project

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

sleep 3m
