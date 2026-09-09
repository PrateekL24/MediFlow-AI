import streamlit as st

from backend.workflows.runner import WorkflowRunner


st.set_page_config(
    page_title="MediFlow AI",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 MediFlow AI")
st.caption("AI Healthcare Administration Assistant")


if "messages" not in st.session_state:
    st.session_state.messages = []


if "workflow_state" not in st.session_state:
    st.session_state.workflow_state = {
        "user_input": "",
        "session_id": "streamlit-session",
        "intent": None,
        "patient_data": {},
        "request_data": {},
        "tool_result": None,
        "workflow_id": None,
        "current_agent": None,
        "awaiting_input": None,
        "messages": [],
        "response": None,
        "patient_lookup": None,
        "selected_patient": None,
        "selected_doctor": None,
        "doctors_found": [],
        "appointment_data": {},
        "document_data": None,
        "next_step": None,
        "workflow_status": "started",
        "last_error": None,
    }


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------------------------------------
# Document Upload Input
# ---------------------------------------

state = st.session_state.workflow_state

if state.get("awaiting_input") == "document_upload":
    if "document_uploader_key" not in st.session_state:
        st.session_state.document_uploader_key = 0

    uploaded_file = st.file_uploader(
        "Upload medical document",
        type=["pdf", "jpg", "jpeg", "png"],
        key=f"document_uploader_{st.session_state.document_uploader_key}",
    )

    if uploaded_file is not None:
        result = WorkflowRunner.run(
            user_input="",
            session_id=state["session_id"],
            existing_state=state,
            uploaded_file=uploaded_file,
        )

        st.session_state.workflow_state = result

        response = result.get(
            "response",
            "Sorry, I couldn't process the document."
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        st.session_state.document_uploader_key += 1
        st.rerun()


# ---------------------------------------
# Chat Input
# ---------------------------------------

if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    state = st.session_state.workflow_state

    result = WorkflowRunner.run(
        user_input=prompt,
        session_id=state["session_id"],
        existing_state=state,
    )

    st.session_state.workflow_state = result

    response = result.get(
        "response",
        "Sorry, I couldn't process your request."
    )

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

    st.rerun()
