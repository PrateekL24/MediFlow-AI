from typing import Optional

from backend.repositories.workflow_repository import WorkflowRepository


class WorkflowService:

    @staticmethod
    def build_workflow_state(state: dict) -> dict:
        """Build the safe, persistable workflow state."""
        return {
            "intent": state.get("intent"),
            "patient_data": state.get("patient_data"),
            "request_data": state.get("request_data"),
            "patient_lookup": state.get("patient_lookup"),
            "selected_patient": state.get("selected_patient"),
            "selected_doctor": state.get("selected_doctor"),
            "doctors_found": state.get("doctors_found"),
            "appointment_data": state.get("appointment_data"),
            "document_data": state.get("document_data"),
            "current_node": state.get("current_node"),
            "current_agent": state.get("current_agent"),
            "awaiting_input": state.get("awaiting_input"),
            "next_step": state.get("next_step"),
            "workflow_status": state.get("workflow_status"),
            "last_error": state.get("last_error")
        }

    @staticmethod
    def start_workflow(workflow_id: str, session_id: str, state: dict):
        state["workflow_status"] = "running"
        return WorkflowRepository.create_workflow(
            workflow_id=workflow_id,
            session_id=session_id,
            workflow_state=WorkflowService.build_workflow_state(state),
            current_agent=state.get("current_agent"),
            current_node=state.get("current_node"),
            status="running"
        )

    @staticmethod
    def save_workflow(workflow_id: str, state: dict, current_node: Optional[str] = None):
        return WorkflowRepository.update_workflow(
            workflow_id=workflow_id,
            workflow_state=WorkflowService.build_workflow_state(state),
            current_agent=state.get("current_agent"),
            current_node=current_node if current_node is not None else state.get("current_node"),
            status=WorkflowService.get_database_status(state.get("workflow_status"))
        )

    @staticmethod
    def get_database_status(workflow_status: Optional[str]) -> str:
        status_mapping = {
            "started": "running",
            "in_progress": "running",
            "waiting_for_user": "paused",
            "completed": "completed",
            "failed": "failed"
        }
        return status_mapping.get(workflow_status, "running")

    @staticmethod
    def get_workflow(workflow_id: str):
        return WorkflowRepository.get_workflow(workflow_id)

    @staticmethod
    def mark_in_progress(workflow_id: str, state: dict, current_node: Optional[str] = None):
        state["workflow_status"] = "in_progress"
        return WorkflowService.save_workflow(workflow_id, state, current_node)

    @staticmethod
    def mark_waiting_for_user(workflow_id: str, state: dict, current_node: Optional[str] = None):
        state["workflow_status"] = "waiting_for_user"
        return WorkflowService.save_workflow(workflow_id, state, current_node)

    @staticmethod
    def mark_completed(workflow_id: str, state: dict, current_node: Optional[str] = None):
        state["workflow_status"] = "completed"
        return WorkflowService.save_workflow(workflow_id, state, current_node)

    @staticmethod
    def mark_failed(workflow_id: str, state: dict, error_message: str, current_node: Optional[str] = None):
        state["workflow_status"] = "failed"
        state["last_error"] = error_message
        return WorkflowService.save_workflow(workflow_id, state, current_node)
