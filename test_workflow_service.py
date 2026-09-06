import uuid

from backend.services.workflow_service import WorkflowService


workflow_id = str(uuid.uuid4())
session_id = "test-session-001"

state = {
    "intent": "book_appointment",
    "patient_data": {
        "first_name": "Test",
        "age": 28,
        "phone": "9999999999"
    },
    "request_data": {
        "doctor_name": "Dr. Ritu Shah",
        "symptom": "back pain"
    },
    "current_agent": "Reception",
    "awaiting_input": "phone",
    "next_step": "appointment",
    "workflow_status": "started",
    "last_error": None
}


print("\n1. Starting workflow...")

result = WorkflowService.start_workflow(
    workflow_id,
    session_id,
    state
)

print(result)


print("\n2. Marking workflow in progress...")

result = WorkflowService.mark_in_progress(
    workflow_id,
    state,
    current_node="reception"
)

print(result)


print("\n3. Marking workflow waiting for user...")

state["awaiting_input"] = "patient_selection"

result = WorkflowService.mark_waiting_for_user(
    workflow_id,
    state,
    current_node="reception"
)

print(result)


print("\n4. Loading workflow from database...")

workflow = WorkflowService.get_workflow(
    workflow_id
)

print(workflow)


print("\n5. Marking workflow completed...")

state["awaiting_input"] = None
state["current_agent"] = None
state["next_step"] = None

result = WorkflowService.mark_completed(
    workflow_id,
    state,
    current_node="appointment"
)

print(result)


print("\n6. Final workflow from database...")

workflow = WorkflowService.get_workflow(
    workflow_id
)

print(workflow)