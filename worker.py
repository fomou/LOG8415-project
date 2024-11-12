from flask import Flask, jsonify,request
from mysql.connector import connect
app = Flask(__name__)
import random
def get_connector():

    connection = connect(
        host='localhost',        # MySQL server address (localhost or IP)
        user='root',             # MySQL username
       # MySQL password
        database='sakila' # Database name
    )
    return connection

@app.route("/ping")
def ping():
    return jsonify({"status": "healthy"}),200

@app.route("/read")
def read_data():
    connection = get_connector()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM test")
    row = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify({"data":row}), 200

@app.route("/write")
def write():
    connection = get_connector()
    cursor = connection.cursor(dictionary=True)
    name = request.args.get("name")
    cursor.execute("CREATE TABLE IF NOT EXISTS test (id INT AUTO_INCREMENT,name VARCHAR(255),PRIMARY KEY (id));")
    cursor.execute(f"INSERT INTO test (name) VALUES ('{name}');")
    row = cursor.fetchall()
    cursor.close()
    connection.commit()
    connection.close()
    return jsonify({'val':row}), 200

@app.route("/table_size")
def get_table_size():
    connection = get_connector()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as size FROM test")
    row = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(row[0]), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) # Adjust port if needed