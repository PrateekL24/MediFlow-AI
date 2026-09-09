import uuid
import traceback

from backend.workflows.state import GraphState
from backend.services.workflow_service import WorkflowService
from backend.services.audit_service import AuditService

from backend.workflows.graph import graph


class WorkflowRunner:

    ACTIVE_NEXT_STEPS = {
        "reception",
        "registration",
        "appointment",
        "document",
    }

    @staticmethod
    def _audit(
        workflow_id: str,
        action: str,
        status: str,
        current_node: str | None = None,
        metadata: dict | None = None,
    ):
        AuditService.record_event(
            workflow_id=workflow_id,
            agent_name="Workflow",
            tool_name="WorkflowRunner",
            action=action,
            status=status,
            metadata={
                "current_node": current_node,
                **(metadata or {}),
            },
        )

    @staticmethod
    def run(
        user_input: str,
        session_id: str,
        existing_state: GraphState | None = None,
        uploaded_file=None,
    ):
        is_new_workflow = existing_state is None
        was_paused = False

        if existing_state is None:
            workflow_id = str(uuid.uuid4())

            state: GraphState = {
                "user_input": user_input,
                "session_id": session_id,
                "intent": None,
                "patient_data": {},
                "request_data": {},
                "tool_result": None,
                "workflow_id": workflow_id,
                "current_node": None,
                "current_agent": None,
                "awaiting_input": None,
                "messages": [],
                "response": None,
                "patient_lookup": None,
                "selected_patient": None,
                "selected_doctor": None,
                "doctors_found": None,
                "appointment_data": None,
                "document_data": None,
                "next_step": None,
                "workflow_status": "started",
                "last_error": None,
            }

            WorkflowService.start_workflow(
                workflow_id=workflow_id,
                session_id=session_id,
                state=state,
            )

            WorkflowRunner._audit(
                workflow_id=workflow_id,
                action="workflow_started",
                status="success",
                current_node=None,
            )

        else:
            state = existing_state
            was_paused = state.get("workflow_status") in {
                "paused",
                "waiting_for_user",
            }
            state["user_input"] = user_input

            workflow_id = state.get("workflow_id")

            if not workflow_id:
                workflow_id = str(uuid.uuid4())
                state["workflow_id"] = workflow_id

                WorkflowService.start_workflow(
                    workflow_id=workflow_id,
                    session_id=session_id,
                    state=state,
                )

                WorkflowRunner._audit(
                    workflow_id=workflow_id,
                    action="workflow_started",
                    status="success",
                    current_node=None,
                )

        try:
            WorkflowService.mark_in_progress(
                workflow_id=workflow_id,
                state=state,
                current_node="entry_router",
            )

            if not is_new_workflow and was_paused:
                WorkflowRunner._audit(
                    workflow_id=workflow_id,
                    action="workflow_resumed",
                    status="success",
                    current_node="entry_router",
                )

            if isinstance(state.get("appointment_data"), dict):
                state["appointment_data"]["_workflow_id"] = workflow_id

            config = None
            if uploaded_file is not None:
                config = {"configurable": {"uploaded_file": uploaded_file}}

            result = graph.invoke(state, config=config)

            result["workflow_id"] = workflow_id
            current_node = result.get("current_node")

            if result.get("awaiting_input"):
                WorkflowService.mark_waiting_for_user(
                    workflow_id=workflow_id,
                    state=result,
                    current_node=current_node,
                )

                WorkflowRunner._audit(
                    workflow_id=workflow_id,
                    action="workflow_paused",
                    status="success",
                    current_node=current_node,
                    metadata={
                        "awaiting_input": result.get("awaiting_input")
                    },
                )

            elif result.get("next_step") in WorkflowRunner.ACTIVE_NEXT_STEPS:
                WorkflowService.mark_in_progress(
                    workflow_id=workflow_id,
                    state=result,
                    current_node=current_node,
                )

            else:
                WorkflowService.mark_completed(
                    workflow_id=workflow_id,
                    state=result,
                    current_node=current_node,
                )

                WorkflowRunner._audit(
                    workflow_id=workflow_id,
                    action="workflow_completed",
                    status="success",
                    current_node=current_node,
                )

            return result

        except Exception as exc:
            error_message = str(exc)
            state["last_error"] = error_message

            WorkflowService.mark_failed(
                workflow_id=workflow_id,
                state=state,
                error_message=error_message,
                current_node=state.get("current_node"),
            )

            WorkflowRunner._audit(
                workflow_id=workflow_id,
                action="workflow_failed",
                status="failure",
                current_node=state.get("current_node"),
                metadata={"error_type": type(exc).__name__},
            )

            print("\n===== WORKFLOW ERROR =====")
            print(error_message)
            traceback.print_exc()
            raise
