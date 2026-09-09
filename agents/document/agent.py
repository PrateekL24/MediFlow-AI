from backend.tools.document_tool import DocumentTool
from backend.workflows.state import GraphState


class DocumentAgent:

    @staticmethod
    def run(state: GraphState, uploaded_file=None):
        selected_patient = state.get("selected_patient")

        if not selected_patient:
            state["current_agent"] = "Reception"
            state["awaiting_input"] = "phone"
            state["response"] = (
                "Before uploading the document, I need to identify the patient. "
                "May I have the patient's mobile number?"
            )
            return state

        if uploaded_file is None:
            state["current_agent"] = "Document"
            state["awaiting_input"] = "document_upload"
            state["response"] = "Please upload the medical document or report."
            return state

        patient_id = selected_patient.get("patient_id")
        if not patient_id:
            state["current_agent"] = "Document"
            state["awaiting_input"] = "document_upload"
            state["response"] = (
                "I couldn't confirm the patient record. Please restart the upload."
            )
            return state

        result = DocumentTool.upload_document(
            patient_id=patient_id,
            document_name=uploaded_file.name,
            content_type=uploaded_file.type or "",
            file_bytes=uploaded_file.getvalue(),
        )

        state["tool_result"] = result

        if not result.get("success"):
            state["current_agent"] = "Document"
            state["awaiting_input"] = "document_upload"
            state["response"] = result.get(
                "message",
                "The document could not be uploaded. Please try again.",
            )
            return state

        state["document_data"] = result.get("data")
        state["awaiting_input"] = None
        state["next_step"] = "continue"
        state["current_agent"] = None
        state["response"] = "The document was uploaded successfully."

        return state
