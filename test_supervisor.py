from agents.supervisor.agent import supervisor_agent

state = {
    "user_input": "Register Prateek, age 28, phone 9876543210",
    "intent": "",
    "patient_data": {},
    "tool_result": None,
    "workflow_id": None,
    "current_agent": "supervisor",
    "messages": [],
    "response": ""
}

result = supervisor_agent(state)

print(result)