from ast import Return
import boto3
import pandas as pd
from datetime import datetime
import psycopg2
import os
import mysql.connector

# Database connection configuration
def get_db_connection():
    return mysql.connector.connect(
        host="meditrack-rds-db.c5mqye4q80uc.us-east-1.rds.amazonaws.com", 
        user="admin",
        password="MeditrackDB",
        database="meditrackDB"
    )

RS_HOST = "meditrack-workgroup.529088288184.us-east-1.redshift-serverless.amazonaws.com"
RS_PORT = "5439"
RS_DBNAME = "dev"
RS_USER = "admin"
RS_PASSWORD = "MeditrackRedshift25*"

# function for aggregate total appointments
def aggregate_total_appointments():
    try:
        # Fetch all appointments from MySQL
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM appointments"
        
        # Aggregate total appointments per doctor
        appointments_df = pd.read_sql(query, connection)
        total_appointments_per_doctor = appointments_df.groupby('doctor_id').size().reset_index(name='total_appointments')
        
        # Fetch doctor names from PostgreSQL
        doctor_ids = total_appointments_per_doctor['doctor_id'].tolist()
        doctor_query = f"SELECT doctor_id, name FROM doctors WHERE doctor_id IN ({','.join(map(str, doctor_ids))})"
        cursor.execute(doctor_query)
        doctors_data = cursor.fetchall()
        doctors_df = pd.DataFrame(doctors_data, columns=['doctor_id', 'doctor_name'])

        appointments_df['doctor_id'] = appointments_df['doctor_id'].astype(int)
        doctors_df['doctor_id'] = doctors_df['doctor_id'].astype(int)
        total_appointments_per_doctor['doctor_id'] = total_appointments_per_doctor['doctor_id'].astype(int)
        
        # Merge with doctor names
        merged_df = total_appointments_per_doctor.merge(doctors_df, on='doctor_id', how='left')
        test = pd.DataFrame(merged_df , columns=['doctor_name', 'total_appointments'])
        
        return test
    
    except Exception as e:
        print("Error connecting to the database:", e)

# function for aggregate doctors per specialty
def aggregate_doctors_per_specialty():
    try:
        # Connect to MySQL
        connection = get_db_connection()
        cursor = connection.cursor()

        doctor_query = "SELECT specialty, COUNT(*) FROM doctors GROUP BY specialty"
        cursor.execute(doctor_query)
        specialty_data = cursor.fetchall()
        
        specialty_df = pd.DataFrame(specialty_data, columns=['specialty', 'doctor_count'])
        
        return specialty_df
    
    except Exception as e:
        print("Error connecting to the database:", e)

# function for aggregate appointments per month
def aggregate_appointments_per_month():

    try:
        # Fetch all appointments from MySQL
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM appointments"
        
        # Convert into dataframe
        appointments_df = pd.read_sql(query, connection)
        
        # Convert appointment date to datetime
        appointments_df['appointment_date'] = pd.to_datetime(appointments_df['appointment_date'])
        
        # Extract month-year and doctor name
        appointments_df['month_year'] = appointments_df['appointment_date'].dt.strftime('%B %Y')
        
        # Group by month_year and doctor
        month_appointments = appointments_df.groupby(['month_year', 'doctor_id']).size().reset_index(name='appointment_count')
        
        # Fetch doctor names from PostgreSQL
        doctor_ids = month_appointments['doctor_id'].tolist()
        doctor_query = f"SELECT doctor_id, name FROM doctors WHERE doctor_id IN ({','.join(map(str, doctor_ids))})"
        cursor.execute(doctor_query)
        doctors_data = cursor.fetchall()
        doctors_df = pd.DataFrame(doctors_data, columns=['doctor_id', 'doctor_name'])

        doctors_df['doctor_id'] = doctors_df['doctor_id'].astype(int)
        month_appointments['doctor_id'] = month_appointments['doctor_id'].astype(int)
        
        # Merge with doctor names
        merged_df = month_appointments.merge(doctors_df, on='doctor_id', how='left')
        
        return merged_df[['month_year', 'doctor_name', 'appointment_count']]
    
    except Exception as e:
        print("Error connecting to the database:", e)

# function for insert Total appointments per doctors
def insert_total_appointments_per_doctor(aggregated_df):

    try:
        conn_rs = psycopg2.connect(
            host = RS_HOST,
            port = RS_PORT,
            dbname = RS_DBNAME,
            user = RS_USER,
            password = RS_PASSWORD
        )
        cur_rs  = conn_rs.cursor()
    
        # Iterate through the DataFrame and insert/update records in Redshift
        for index, row in aggregated_df.iterrows():
            doctor_name = row['doctor_name']
            total_appointments = row['total_appointments']

            # Step 1: Update existing records
            update_query = """
                UPDATE total_appointments_per_doctor
                SET total_appointments = %s
                WHERE doctor_name = %s;
            """
            cur_rs.execute(update_query, (total_appointments, doctor_name))

            # Step 2: If no records were updated, insert the new record
            insert_query = """
                INSERT INTO total_appointments_per_doctor (doctor_name, total_appointments)
                SELECT %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM total_appointments_per_doctor WHERE doctor_name = %s
                );
            """
            cur_rs.execute(insert_query, (doctor_name, total_appointments, doctor_name))

        # Commit and close the connection
        conn_rs.commit()
        cur_rs.close()
        conn_rs.close()

    except Exception as e:
        print("Error connecting to the database:", e)

# function for insert appointments per month for per doctor
def insert_appointments_per_month_per_doctor(aggregated_df):

    try:
        conn_rs = psycopg2.connect(
            host = RS_HOST,
            port = RS_PORT,
            dbname = RS_DBNAME,
            user = RS_USER,
            password = RS_PASSWORD
        )

        cur_rs  = conn_rs.cursor()
    
        # Iterate through the DataFrame and insert/update records in Redshift
        for index, row in aggregated_df.iterrows():
            month_year = row['month_year']
            doctor_name = row['doctor_name']
            total_appointments = row['appointment_count']

            # Step 1: Update existing records
            update_query = """
                UPDATE appointments_per_month_per_doctor
                SET appointment_count  = %s
                WHERE month_year = %s AND doctor_name = %s;
            """
            cur_rs.execute(update_query, (total_appointments, month_year, doctor_name))

            # Step 2: If no records were updated, insert the new record
            insert_query = """
                INSERT INTO appointments_per_month_per_doctor (month_year, doctor_name, appointment_count )
                SELECT %s, %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM appointments_per_month_per_doctor 
                    WHERE month_year = %s AND doctor_name = %s
                );
            """
            cur_rs.execute(insert_query, (month_year, doctor_name, total_appointments, month_year, doctor_name))

        # Commit and close the connection
        conn_rs.commit()
        cur_rs.close()
        conn_rs.close()
    
    except Exception as e:
        print("Error connecting to the database:", e)


# function for insert doctors per specialty
def insert_doctors_per_speciality(doctors_per_speciality_df):
    # Assuming you already have a connection to Redshift
    try:
        conn_rs = psycopg2.connect(
            host = RS_HOST,
            port = RS_PORT,
            dbname = RS_DBNAME,
            user = RS_USER,
            password = RS_PASSWORD
        )

        cur_rs  = conn_rs.cursor()
    
        # Iterate through the DataFrame and insert/update records in Redshift
        for index, row in doctors_per_speciality_df.iterrows():
            specialty = row["specialty"]
            doctor_count = row["doctor_count"]

            # Use a Redshift-compatible UPSERT (MERGE) query
            merge_query = f"""
                BEGIN;

                DELETE FROM doctors_per_speciality 
                WHERE specialty = %s;

                INSERT INTO doctors_per_speciality (specialty, doctor_count)
                VALUES (%s, %s);

                COMMIT;
            """
            cur_rs.execute(merge_query, (specialty, specialty, doctor_count))

        # Commit and close the connection
        conn_rs.commit()
        cur_rs.close()
        conn_rs.close()

    except Exception as e:
        print("Error connecting to the database:", e)


def main():
    aggregated_df = aggregate_total_appointments()
    insert_total_appointments_per_doctor(aggregated_df)

    aggregated_df = aggregate_appointments_per_month()
    insert_appointments_per_month_per_doctor(aggregated_df)

    doctors_per_speciality_df = aggregate_doctors_per_specialty()
    insert_doctors_per_speciality(doctors_per_speciality_df)

if __name__ == "__main__":
    main()