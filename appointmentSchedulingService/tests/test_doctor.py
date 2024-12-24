import requests

BASE_URL = "http://localhost:8080"  # Update with your service URL

def test_patient_operations():
    # Step 1: Add a new doctor
    data = {
    "name": "Dr. Testing",
    "specialty": 29,
    "email": "testing@gmail.com",
    "contact" : "1234567890",
    "availability_hours": "5 PM - 10 PM"
    }

    response = requests.post(f"{BASE_URL}/add_doctor", json=data)
    assert response.status_code == 201  # Ensure the request was successful

    # Step 2: Extract doctor_id from the response
    doctor_id = response.json().get("id")
    assert doctor_id is not None, "Doctor ID should be returned"

    # Step 3: View the doctor using the doctor_id
    response = requests.get(f"{BASE_URL}/get_doctors")
    assert response.status_code == 200  # Ensure we get a valid response
    doctors = response.json()
    assert any(d["id"] == doctor_id for d in doctors), "Patient not found in patient list"

    # Step 4: Delete the doctor using the doctor_id
    response = requests.delete(f"{BASE_URL}/delete_doctor/{doctor_id}")
    assert response.status_code == 200  # Ensure the delete was successful