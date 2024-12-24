import requests

BASE_URL = "http://localhost:8080"  # Update with your service URL

def test_patient_operations():
    # Step 1: Add a new patient
    data = {
    "name": "Testing",
    "age": 29,
    "gender": "Female",
    "address": "Testing",
    "email": "testing@gmail.com",
    "contact_number" : "1234567891",
    "medical_history": [
        "Allergies: Testing",
        "Chronic Conditions: Testing"]
    }

    response = requests.post(f"{BASE_URL}/add_patient", json=data)
    assert response.status_code == 201  # Ensure the request was successful

    # Step 2: Extract patient_id from the response
    patient_id = response.json().get("id")
    assert patient_id is not None, "Patient ID should be returned"

    # Step 3: View the patient using the patient_id
    response = requests.get(f"{BASE_URL}/get_patients")
    assert response.status_code == 200  # Ensure we get a valid response
    patients = response.json()
    assert any(p["id"] == patient_id for p in patients), "Patient not found in patient list"

    # Step 4: Delete the patient using the patient_id
    response = requests.delete(f"{BASE_URL}/delete_patient/{patient_id}")
    assert response.status_code == 200  # Ensure the delete was successful