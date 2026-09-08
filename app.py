import threading
from flask import Flask, jsonify, request

def create_patient_service():
    app = Flask("PatientService")
    patients = {}
    counter = 1

    @app.route('/api/patients', methods=['POST'])
    def create_patient():
        nonlocal counter
        data = request.json
        patient = {
            "id": counter,
            "fullName": data.get("fullName"),
            "dateOfBirth": data.get("dateOfBirth"),
            "gender": data.get("gender"),
            "phone": data.get("phone"),
            "address": data.get("address"),
            "insuranceId": data.get("insuranceId")
        }
        patients[counter] = patient
        counter += 1
        return jsonify(patient), 201

    @app.route('/api/patients', methods=['GET'])
    def get_patients():
        return jsonify(list(patients.values())), 200

    @app.route('/api/patients/<int:id>', methods=['GET'])
    def get_patient(id):
        patient = patients.get(id)
        if patient:
            return jsonify(patient), 200
        return jsonify({"message": "Patient not found"}), 404

    @app.route('/api/patients/<int:id>', methods=['PUT'])
    def update_patient(id):
        patient = patients.get(id)
        if not patient:
            return jsonify({"message": "Patient not found"}), 404
        data = request.json
        patient.update({
            "fullName": data.get("fullName", patient["fullName"]),
            "dateOfBirth": data.get("dateOfBirth", patient["dateOfBirth"]),
            "gender": data.get("gender", patient["gender"]),
            "phone": data.get("phone", patient["phone"]),
            "address": data.get("address", patient["address"]),
            "insuranceId": data.get("insuranceId", patient["insuranceId"])
        })
        return jsonify(patient), 200

    @app.route('/api/patients/<int:id>', methods=['DELETE'])
    def delete_patient(id):
        if id in patients:
            del patients[id]
            return jsonify({"message": "Patient deleted successfully"}), 200
        return jsonify({"message": "Patient not found"}), 404

    return app

def create_doctor_service():
    app = Flask("DoctorService")
    doctors = {}
    counter = 1

    @app.route('/api/doctors', methods=['POST'])
    def create_doctor():
        nonlocal counter
        data = request.json
        doctor = {
            "id": counter,
            "fullName": data.get("fullName"),
            "specialty": data.get("specialty"),
            "phone": data.get("phone"),
            "email": data.get("email")
        }
        doctors[counter] = doctor
        counter += 1
        return jsonify(doctor), 201

    @app.route('/api/doctors', methods=['GET'])
    def get_doctors():
        return jsonify(list(doctors.values())), 200

    @app.route('/api/doctors/<int:id>', methods=['GET'])
    def get_doctor(id):
        doctor = doctors.get(id)
        if doctor:
            return jsonify(doctor), 200
        return jsonify({"message": "Doctor not found"}), 404

    @app.route('/api/doctors/<int:id>', methods=['PUT'])
    def update_doctor(id):
        doctor = doctors.get(id)
        if not doctor:
            return jsonify({"message": "Doctor not found"}), 404
        data = request.json
        doctor.update({
            "fullName": data.get("fullName", doctor["fullName"]),
            "specialty": data.get("specialty", doctor["specialty"]),
            "phone": data.get("phone", doctor["phone"]),
            "email": data.get("email", doctor["email"])
        })
        return jsonify(doctor), 200

    @app.route('/api/doctors/<int:id>', methods=['DELETE'])
    def delete_doctor(id):
        if id in doctors:
            del doctors[id]
            return jsonify({"message": "Doctor deleted successfully"}), 200
        return jsonify({"message": "Doctor not found"}), 404

    return app

def create_appointment_service():
    app = Flask("AppointmentService")
    appointments = {}
    counter = 1

    @app.route('/api/appointments', methods=['POST'])
    def create_appointment():
        nonlocal counter
        data = request.json
        appointment = {
            "id": counter,
            "patientId": data.get("patientId"),
            "doctorId": data.get("doctorId"),
            "dateTime": data.get("dateTime"),
            "status": data.get("status", "PENDING")
        }
        appointments[counter] = appointment
        counter += 1
        return jsonify(appointment), 201

    @app.route('/api/appointments', methods=['GET'])
    def get_appointments():
        return jsonify(list(appointments.values())), 200

    @app.route('/api/appointments/<int:id>', methods=['GET'])
    def get_appointment(id):
        appointment = appointments.get(id)
        if appointment:
            return jsonify(appointment), 200
        return jsonify({"message": "Appointment not found"}), 404

    @app.route('/api/appointments/<int:id>', methods=['PUT'])
    def update_appointment(id):
        appointment = appointments.get(id)
        if not appointment:
            return jsonify({"message": "Appointment not found"}), 404
        data = request.json
        appointment.update({
            "patientId": data.get("patientId", appointment["patientId"]),
            "doctorId": data.get("doctorId", appointment["doctorId"]),
            "dateTime": data.get("dateTime", appointment["dateTime"]),
            "status": data.get("status", appointment["status"])
        })
        return jsonify(appointment), 200

    @app.route('/api/appointments/<int:id>', methods=['DELETE'])
    def delete_appointment(id):
        if id in appointments:
            del appointments[id]
            return jsonify({"message": "Appointment deleted successfully"}), 200
        return jsonify({"message": "Appointment not found"}), 404

    return app

def create_medical_record_service():
    app = Flask("MedicalRecordService")
    records = {}
    counter = 1

    @app.route('/api/medical-records', methods=['POST'])
    def create_record():
        nonlocal counter
        data = request.json
        record = {
            "id": counter,
            "patientId": data.get("patientId"),
            "diagnosis": data.get("diagnosis"),
            "treatment": data.get("treatment"),
            "date": data.get("date")
        }
        records[counter] = record
        counter += 1
        return jsonify(record), 201

    @app.route('/api/medical-records', methods=['GET'])
    def get_records():
        return jsonify(list(records.values())), 200

    @app.route('/api/medical-records/<int:id>', methods=['GET'])
    def get_record(id):
        record = records.get(id)
        if record:
            return jsonify(record), 200
        return jsonify({"message": "Medical record not found"}), 404

    @app.route('/api/medical-records/<int:id>', methods=['PUT'])
    def update_record(id):
        record = records.get(id)
        if not record:
            return jsonify({"message": "Medical record not found"}), 404
        data = request.json
        record.update({
            "patientId": data.get("patientId", record["patientId"]),
            "diagnosis": data.get("diagnosis", record["diagnosis"]),
            "treatment": data.get("treatment", record["treatment"]),
            "date": data.get("date", record["date"])
        })
        return jsonify(record), 200

    @app.route('/api/medical-records/<int:id>', methods=['DELETE'])
    def delete_record(id):
        if id in records:
            del records[id]
            return jsonify({"message": "Medical record deleted successfully"}), 200
        return jsonify({"message": "Medical record not found"}), 404

    return app

def create_pharmacy_service():
    app = Flask("PharmacyService")
    medicines = {}
    counter = 1

    @app.route('/api/pharmacies', methods=['POST'])
    def create_medicine():
        nonlocal counter
        data = request.json
        medicine = {
            "id": counter,
            "name": data.get("name"),
            "manufacturer": data.get("manufacturer"),
            "price": data.get("price"),
            "quantity": data.get("quantity")
        }
        medicines[counter] = medicine
        counter += 1
        return jsonify(medicine), 201

    @app.route('/api/pharmacies', methods=['GET'])
    def get_medicines():
        return jsonify(list(medicines.values())), 200

    @app.route('/api/pharmacies/<int:id>', methods=['GET'])
    def get_medicine(id):
        medicine = medicines.get(id)
        if medicine:
            return jsonify(medicine), 200
        return jsonify({"message": "Medicine not found"}), 404

    @app.route('/api/pharmacies/<int:id>', methods=['PUT'])
    def update_medicine(id):
        medicine = medicines.get(id)
        if not medicine:
            return jsonify({"message": "Medicine not found"}), 404
        data = request.json
        medicine.update({
            "name": data.get("name", medicine["name"]),
            "manufacturer": data.get("manufacturer", medicine["manufacturer"]),
            "price": data.get("price", medicine["price"]),
            "quantity": data.get("quantity", medicine["quantity"])
        })
        return jsonify(medicine), 200

    @app.route('/api/pharmacies/<int:id>', methods=['DELETE'])
    def delete_medicine(id):
        if id in medicines:
            del medicines[id]
            return jsonify({"message": "Medicine deleted successfully"}), 200
        return jsonify({"message": "Medicine not found"}), 404

    return app

def run_service(app, port):
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    services = [
        (create_patient_service(), 8081),
        (create_doctor_service(), 8082),
        (create_appointment_service(), 8083),
        (create_medical_record_service(), 8084),
        (create_pharmacy_service(), 8085)
    ]
    
    threads = []
    for app, port in services:
        t = threading.Thread(target=run_service, args=(app, port))
        t.daemon = True
        t.start()
        threads.append(t)
        print(f"Service {app.name} is running on port {port}...")

    for t in threads:
        t.join()
