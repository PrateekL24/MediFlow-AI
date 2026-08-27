import streamlit as st

from backend.workflows.graph import graph


# ---------------------------------------
# Page Configuration
# ---------------------------------------

st.set_page_config(
    page_title="MediFlow AI",
    page_icon="🏥",
    layout="wide"
)


st.title("🏥 MediFlow AI")
st.caption("AI Healthcare Administration Assistant")


# ---------------------------------------
# Initialize Session
# ---------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


if "workflow_state" not in st.session_state:

    st.session_state.workflow_state = {
        "user_input": "",
        "session_id": "streamlit-session",

        "intent": "",
        "patient_data": {},
        "request_data": {},

        "tool_result": None,

        "workflow_id": None,
        "current_agent": None,

        "awaiting_input": None,

        "messages": [],

        "response": "",

        "patient_lookup": None,
        "selected_patient": None,

        "selected_doctor": None,
        "doctors_found": [],
        "appointment_data": {},

        "next_step": None
    }


# ---------------------------------------
# Display Chat History
# ---------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------------------------------------
# Chat Input
# ---------------------------------------

if prompt := st.chat_input(
    "How can I help you today?"
):

    # Show user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)


    # ---------------------------------------
    # Update Existing Workflow State
    # ---------------------------------------

    state = st.session_state.workflow_state

    state["user_input"] = prompt


    # ---------------------------------------
    # Run LangGraph
    # ---------------------------------------

    result = graph.invoke(state)


    # ---------------------------------------
    # Save Updated State
    # ---------------------------------------

    st.session_state.workflow_state = result


    # ---------------------------------------
    # Get Response
    # ---------------------------------------

    response = result.get(
        "response",
        "Sorry, I couldn't process your request."
    )


    # ---------------------------------------
    # Show Assistant Response
    # ---------------------------------------

    with st.chat_message("assistant"):
        st.markdown(response)


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )
