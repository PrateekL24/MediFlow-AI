from backend.workflows.graph import graph

import time

from backend.workflows.graph import graph


print("\n===== GRAPH TEST: DOCTOR FEE =====")

state = {
    "user_input": "",
    "session_id": "test-session",

    "intent": "doctor_fee",

    "patient_data": {},
    "request_data": {
        "doctor_name": "Dr. Ritu Shah",
        "symptom": ""
    },

    "tool_result": None,

    "workflow_id": None,
    "current_agent": None,

    "awaiting_input": None,

    "messages": [],

    "response": "",

    "patient_lookup": None,
    "selected_patient": None,

    "next_step": None
}


start = time.perf_counter()

result = graph.invoke(state)

elapsed = time.perf_counter() - start


print("\n===== FINAL RESPONSE =====")
print(result.get("response"))

print(
    f"\n===== GRAPH EXECUTION TIME: "
    f"{elapsed:.2f} sec ====="
)

print("\n===== GRAPH TEST: DOCTOR FEE =====")

state = {
    "user_input": "",
    "session_id": "test-session",

    "intent": "doctor_fee",

    "patient_data": {},
    "request_data": {
        "doctor_name": "Dr. Ritu Shah",
        "symptom": ""
    },

    "tool_result": None,

    "workflow_id": None,
    "current_agent": None,

    "awaiting_input": None,

    "messages": [],

    "response": "",

    "patient_lookup": None,
    "selected_patient": None,

    "next_step": None
}


result = graph.invoke(state)


print("\n===== FINAL RESPONSE =====")
print(result.get("response"))