from flask import Flask, request, jsonify, render_template
import mysql.connector

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
@app.route('/')
def index():
    return render_template('index.html')

# API route to add a new patient
@app.route('/api/patients', methods=['POST'])
def add_patient():
    data = request.json
    name = data.get('name')
    age = data.get('age')
    gender = data.get('gender')
    contact_number = data.get('contact_number')
    email = data.get('email')
    medical_history = data.get('medical_history')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO patients (name, age, gender, medical_history, contact_number, email)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, age, gender, medical_history, contact_number, email))
        connection.commit()

        return jsonify({"message": "Patient record added successfully."}), 201

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"message": "Failed to add patient record."}), 500

    finally:
        cursor.close()
        connection.close()

# API route to get all patients
@app.route('/api/patients', methods=['GET'])
def get_patients():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM patients"
        cursor.execute(query)
        results = cursor.fetchall()

        return jsonify(results), 200

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"message": "Failed to retrieve patient records."}), 500

    finally:
        cursor.close()
        connection.close()

# API route to update a patient record
@app.route('/api/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    data = request.json

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        UPDATE patients
        SET name = %s, age = %s, gender = %s, medical_history = %s, contact_number = %s, email = %s
        WHERE patient_id = %s
        """
        cursor.execute(query, (
            data.get('name'),
            data.get('age'),
            data.get('gender'),
            data.get('medical_history'),
            data.get('contact_number'),
            data.get('email'),
            patient_id
        ))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Patient record not found."}), 404

        return jsonify({"message": "Patient record updated successfully."}), 200

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"message": "Failed to update patient record."}), 500

    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
