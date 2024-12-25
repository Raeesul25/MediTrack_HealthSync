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
@app.route('/appointment')
def index():
    return render_template('index.html')

# API to get all available doctors
@app.route('/doctor/get', methods=['GET'])
def get_doctors():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM doctors"
        cursor.execute(query)
        results = cursor.fetchall()

        return jsonify(results), 200

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"message": "Failed to retrieve doctors."}), 500


# API to add a new doctor
@app.route('/doctor/add', methods=['POST'])
def add_doctor():
    data = request.json
    name = data.get('name')
    specialty = data.get('specialty')
    email = data.get('email')
    contact_number = data.get('contact_number')
    availability_hours = data.get('availability_hours')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO doctors (name, specialty, email, contact_number, availability_hours)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, specialty, email, contact_number, availability_hours))
        connection.commit()

        return jsonify({"message": "Doctor added successfully."}), 201

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"message": "Failed to add doctor."}), 500


# API to update doctor information
@app.route('/doctor/update/<int:doctor_id>', methods=['PUT'])
def update_doctor(doctor_id):
    data = request.json

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        UPDATE doctors
        SET name = %s, specialty = %s, email = %s, contact_number = %s, availability_hours = %s
        WHERE doctor_id = %s
        """
        cursor.execute(query, (
            data.get('name'),
            data.get('specialty'),
            data.get('email'),
            data.get('contact_number'),
            data.get('availability_hours'),
            doctor_id
        ))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Doctor not found."}), 404

        return jsonify({"message": "Doctor updated successfully."}), 200

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"message": "Failed to update doctor."}), 500


# API to delete a doctor
@app.route('/doctor/delete/<int:doctor_id>', methods=['DELETE'])
def delete_doctor(doctor_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "DELETE FROM doctors WHERE doctor_id = %s"
        cursor.execute(query, (doctor_id,))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Doctor not found."}), 404

        return jsonify({"message": "Doctor deleted successfully."}), 200

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"message": "Failed to delete doctor."}), 500


# API to book an appointment
@app.route('/appointment/add', methods=['POST'])
def book_appointment():
    data = request.json
    patient_id = data.get('patient_id')
    doctor_id = data.get('doctor_id')
    appointment_date = data.get('appointment_date')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the doctor is available
        availability_query = """
        SELECT * FROM doctors WHERE doctor_id = %s
        """
        cursor.execute(availability_query, (doctor_id,))
        doctor = cursor.fetchone()

        if not doctor:
            return jsonify({"message": "Doctor not found."}), 404

        # Check if the patient is available
        availability_query = """
        SELECT * FROM patients WHERE patient_id = %s
        """
        cursor.execute(availability_query, (patient_id,))
        doctor = cursor.fetchone()

        if not doctor:
            return jsonify({"message": "Patient not found."}), 404

        # Insert the appointment
        insert_query = """
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, status)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (patient_id, doctor_id, appointment_date, 'Scheduled'))
        connection.commit()

        return jsonify({"message": "Appointment booked successfully."}), 201

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"message": "Failed to book appointment."}), 500


# API to view all appointments
@app.route('/appointment/get', methods=['GET'])
def get_appointments():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT appointments.appointment_id, patients.name AS patient_name, 
               doctors.name AS doctor_name, appointments.appointment_date
        FROM appointments
        JOIN patients ON appointments.patient_id = patients.patient_id
        JOIN doctors ON appointments.doctor_id = doctors.doctor_id
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return jsonify(results), 200

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"message": "Failed to retrieve appointments."}), 500


# API to delete an appointment
@app.route('/appointment/delete/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "DELETE FROM appointments WHERE appointment_id = %s"
        cursor.execute(query, (appointment_id,))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Appointment not found."}), 404

        return jsonify({"message": "Appointment deleted successfully."}), 200

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"message": "Failed to delete appointment."}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
