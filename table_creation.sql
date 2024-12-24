use meditrackDB;

-- Step 1: create tables
CREATE TABLE patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    medical_history TEXT,
    contact_number VARCHAR(15),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialty VARCHAR(100),
    contact_number VARCHAR(15),
    email VARCHAR(100),
    availability_hours VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    status ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_status ENUM('Pending', 'Sent', 'Failed') DEFAULT 'Pending',
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

-- Step 2: Insert patient records
INSERT INTO patients (name, age, gender, medical_history, contact_number, email)
VALUES 
('John Doe', 34, 'Male', JSON_ARRAY('Allergies: Dust', 'Chronic Conditions: Asthma'), '1234567890', 'john.doe@example.com'),
('Jane Smith', 28, 'Female', JSON_ARRAY('Allergies: Pollen'), '0987654321', 'jane.smith@example.com'),
('Emily White', 45, 'Female', JSON_ARRAY('Chronic Conditions: Diabetes', 'Allergies: Peanuts'), '1122334455', 'emily.white@example.com');

select * from patients;

-- Step 3: Insert doctor records
INSERT INTO doctors (name, specialty, contact_number, email, availability_hours)
VALUES 
('Dr. Robert Brown', 'Cardiology', '9988776655', 'robert.brown@example.com', '9 AM - 5 PM'),
('Dr. Sarah Johnson', 'Cardiology', '8877665544', 'sarah.johnson@example.com', '10 AM - 6 PM'),
('Dr. Michael Green', 'Dermatology', '7766554433', 'michael.green@example.com', '11 AM - 4 PM'),
('Dr. Laura Davis', 'Neurology', '6655443322', 'laura.davis@example.com', '1 PM - 8 PM');

select * from doctors;

-- Step 4: Insert appointment records
INSERT INTO appointments (patient_id, doctor_id, appointment_date, status)
VALUES 
(1, 1, '2024-01-10 10:30:00', 'Scheduled'),
(2, 2, '2024-01-12 11:00:00', 'Scheduled'),
(3, 3, '2024-01-15 14:00:00', 'Scheduled'),
(1, 4, '2024-01-18 16:30:00', 'Scheduled');

select * from appointments;

-- Step 5: Insert notification records
INSERT INTO notifications (patient_id, message, delivery_status)
VALUES 
(1, 'Your appointment is scheduled for 2024-01-10 at 10:30 AM', 'Sent'),
(3, 'Your appointment is scheduled for 2024-01-15 at 2:00 PM', 'Sent');

select * from notifications;

CREATE TABLE total_appointments_per_doctor (
    doctor_name VARCHAR(255) NOT NULL,
    total_appointments INT NOT NULL,
    PRIMARY KEY (doctor_name)
);

CREATE TABLE appointments_per_month_per_doctor (
    month_year VARCHAR(50) NOT NULL,
    doctor_name VARCHAR(255) NOT NULL,
    appointment_count INT NOT NULL,
    PRIMARY KEY (month_year, doctor_name)
);

CREATE TABLE doctors_per_speciality (
    specialty VARCHAR(255) NOT NULL,
    doctor_count INT NOT NULL,
    PRIMARY KEY (specialty)
);

SELECT * FROM total_appointments_per_doctor;
SELECT * FROM appointments_per_month_per_doctor;
SELECT * FROM doctors_per_speciality;