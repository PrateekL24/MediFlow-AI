from agents.doctor.agent import DoctorAgent


print("\n===== TEST 1: DOCTOR RECOMMENDATION =====")

state = {
    "intent": "doctor_recommendation",
    "request_data": {
        "doctor_name": "",
        "symptom": "headache"
    },
    "response": ""
}

result = DoctorAgent.run(state)

print(result["response"])


print("\n===== TEST 2: DOCTOR FEE =====")

state = {
    "intent": "doctor_fee",
    "request_data": {
        "doctor_name": "Dr. Ritu Shah",
        "symptom": ""
    },
    "response": ""
}

result = DoctorAgent.run(state)

print(result["response"])


print("\n===== TEST 3: DOCTOR AVAILABILITY =====")

state = {
    "intent": "doctor_availability",
    "request_data": {
        "doctor_name": "Dr. Ritu Shah",
        "symptom": ""
    },
    "response": ""
}

result = DoctorAgent.run(state)

print(result["response"])