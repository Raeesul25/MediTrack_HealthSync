from flask import Flask, request, jsonify, render_template
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Database connection configuration
def get_db_connection():
    return mysql.connector.connect(
        host="meditrack-rds-db.c5mqye4q80uc.us-east-1.rds.amazonaws.com", 
        user="admin",
        password="MeditrackDB",
        database="meditrackDB"
    )

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
        connection = get_db_connection()
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

    finally:
        cursor.close()
        connection.close()

# API to retrieve all notifications
@app.route('/notification/get', methods=['GET'])
def get_notifications():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM notifications"
        cursor.execute(query)
        results = cursor.fetchall()

        return jsonify(results), 200

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"message": "Failed to retrieve notifications."}), 500

    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
