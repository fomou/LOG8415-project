#!/bin/bash
#sysbench oltp_read_only --table-size=1000 --mysql-db=sakila --mysql-user=root prepare
sysbench oltp_read_only --table-size=1000 --mysql-db=sakila --mysql-user=root prepare
sysbench oltp_read_only --table-size=100000 --threads=6 --max-time=60 --max-requests=0 --mysql-db=sakila --mysql-user=root run > /home/ubuntu/results.txt
sysbench oltp_read_only --mysql-db=sakila --mysqluser=root --my-sql-password=root cleanup