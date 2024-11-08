#!/bin/bash

# Install MySQL Server and Sysbench
sudo apt-get update
sudo apt-get install mysql-server sysbench python3-venv -y

# Download Sakila database
wget https://downloads.mysql.com/docs/sakila-db.tar.gz -O /home/ubuntu/sakila-db.tar.gz
tar -xvf /home/ubuntu/sakila-db.tar.gz -C /home/ubuntu/

# Upload Sakila database to MySQL
mysql -u root -e "SOURCE /home/ubuntu/sakila-db/sakila-schema.sql;"
mysql -u root -e "SOURCE /home/ubuntu/sakila-db/sakila-data.sql;"
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';"

# Benchmark using Sysbench
# Using table size of 100 000, 6 threads and maximum time of 60 seconds
# Writing results in /home/ubuntu/results.txt
sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --mysql-user=root prepare
sysbench oltp_read_write --table-size=100000 --threads=6 --max-time=60 --max-requests=0 --mysql-db=sakila --mysql-user=root run > /home/ubuntu/results.txt
sysbench oltp_read_write --mysql-db=sakila --mysql-user=root --my-sql-password=root cleanup
cd /home/ubuntu
git clone https://github.com/fomou/LOG8415-project.git

cd LOG8415-project

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 worker.py
