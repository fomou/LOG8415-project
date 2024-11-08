from flask import Flask, jsonify
from mysql.connector import connect
app = Flask(__name__)

def get_connector():

    connection = connect(
        host='localhost',        # MySQL server address (localhost or IP)
        user='root',             # MySQL username

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
    cursor.execute("SELECT count(*) FROM city;")
    row = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify({"data":row}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) # Adjust port if needed