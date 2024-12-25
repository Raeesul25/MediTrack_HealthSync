from flask import Flask, request, jsonify, render_template
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Database connection configuration
MYSQL_HOST = "meditrack-rds-db.c5mqye4q80uc.us-east-1.rds.amazonaws.com"
MYSQL_USER = "admin"
MYSQL_PWD = "MeditrackDB"
MYSQL_DB = "meditrackDB"
PORT = "3306"

# Route for the front-end page
@app.route('/notification')
def index():
    return render_template('index.html')

# API to send a notification
@app.route('/notification/add', methods=['POST'])
def send_notification():
    data = request.json
    patient_id = data.get('patient_id')
    message = data.get('message')

    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PWD,
            database=MYSQL_DB,
            port=PORT
        )
        cursor = connection.cursor()

        # Check if the patient is available
        availability_query = """
        SELECT * FROM patients WHERE patient_id = %s
        """
        cursor.execute(availability_query, (patient_id,))
        doctor = cursor.fetchone()

        if not doctor:
            return jsonify({"message": "Patient not found."}), 404

        query = """
        INSERT INTO notifications (patient_id, message, sent_at, delivery_status)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (patient_id, message, datetime.now(), 'Sent'))
        connection.commit()

        return jsonify({"message": "Notification sent successfully."}), 201

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"message": "Failed to send notification."}), 500

# API to retrieve all notifications
@app.route('/notification/get', methods=['GET'])
def get_notifications():
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PWD,
            database=MYSQL_DB,
            port=PORT
        )
        cursor = connection.cursor()

        query = "SELECT * FROM notifications"
        cursor.execute(query)
        results = cursor.fetchall()

        return jsonify(results), 200

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"message": "Failed to retrieve notifications."}), 500

    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
