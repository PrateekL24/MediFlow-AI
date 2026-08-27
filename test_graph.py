from backend.workflows.graph import graph

state = {
    "user_input": "Register Rahul ",
    "session_id": "test-session-1",
    "intent": "",
    "patient_data": {},
    "tool_result": None,
    "workflow_id": None,
    "current_agent": "",
    "messages": [],
    "response": ""
}

result = graph.invoke(state)

print("\n===== FINAL STATE =====")
print(result)