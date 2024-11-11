USER_DATA_WORKERS = '''
#!/bin/bash
sudo apt update -y
sudo apt install docker.io -y
sudo apt install docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker

cat << 'EOF' > /home/ubuntu/Dockerfile
FROM ubuntu:14.04
RUN apt-get update
RUN apt-get install mysql-server sysbench, python3, python3-venv -y

# Download Sakila database
RUN wget https://downloads.mysql.com/docs/sakila-db.tar.gz -O /home/ubuntu/sakila-db.tar.gz
RUN tar -xvf /home/ubuntu/sakila-db.tar.gz -C /home/ubuntu/

# Upload Sakila database to MySQL
RUN sudo service mysql start

RUN echo -e "\nn\nn\nn\nY\nn\n" | sudo mysql_secure_installation

RUN sudo mysql -u root -e "SOURCE /home/ubuntu/sakila-db/sakila-schema.sql;"
RUN sudo mysql -u root -e "SOURCE /home/ubuntu/sakila-db/sakila-data.sql;"
RUN sudo mysql -u root -e "USE sakila; CREATE USER 'root'@'localhost' IDENTIFIED BY 'root'; GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY 'root'; FLUSH PRIVILEGES;" > /home/ubuntu/db_setup.log 2>&1,
RUN sudo mysql -u root -e "USE sakila; CREATE USER 'root'@'%' IDENTIFIED BY 'root'; GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'root'; FLUSH PRIVILEGES;" > /home/ubuntu/db_setup.log 2>&1,


# Benchmark using Sysbench
# Using table size of 100 000, 6 threads and maximum time of 60 seconds
# Writing results in /home/ubuntu/results.txt
RUN sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --mysql-user=root --mysql-password=root prepare
RUN sysbench oltp_read_write --table-size=100000 --threads=6 --max-time=60 --max-requests=0 --mysql-db=sakila --mysql-user=root --mysql-password=root run > /home/ubuntu/results.txt
RUN sysbench oltp_read_write --mysql-db=sakila --mysql-user=root --mysql-password=root cleanup
RUN cd /home/ubuntu
RUN git clone https://github.com/fomou/LOG8415-project.git

WORKDIR LOG8415-project

RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python3", "worker.py"]
EOF

sudo docker build -t worker . && docker run worker
'''