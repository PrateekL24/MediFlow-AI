import uuid
import traceback

from backend.workflows.state import GraphState
from backend.services.workflow_service import WorkflowService

from backend.workflows.graph import graph


class WorkflowRunner:

    # These values mean the workflow has another business step to execute.
    # Values such as "continue" mean the current interaction is complete.
    ACTIVE_NEXT_STEPS = {
        "reception",
        "registration",
        "appointment"
    }

    @staticmethod
    def run(
        user_input: str,
        session_id: str,
        existing_state: GraphState | None = None
    ):

        # ---------------------------------------
        # Create a new state or continue existing
        # workflow
        # ---------------------------------------

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

                "next_step": None,

                "workflow_status": "started",
                "last_error": None
            }

            # -----------------------------------
            # Create workflow in database
            # -----------------------------------

            WorkflowService.start_workflow(
                workflow_id=workflow_id,
                session_id=session_id,
                state=state
            )

        else:

            # ---------------------------------------
            # Continue existing workflow
            # ---------------------------------------

            state = existing_state
            state["user_input"] = user_input

            workflow_id = state.get(
                "workflow_id"
            )

            if not workflow_id:
                workflow_id = str(uuid.uuid4())
                state["workflow_id"] = workflow_id

                WorkflowService.start_workflow(
                    workflow_id=workflow_id,
                    session_id=session_id,
                    state=state
                )

        try:

            # ---------------------------------------
            # Workflow is actively running
            # ---------------------------------------

            WorkflowService.mark_in_progress(
                workflow_id=workflow_id,
                state=state,
                current_node="entry_router"
            )

            # ---------------------------------------
            # Execute LangGraph
            # ---------------------------------------

            result = graph.invoke(state)

            # ---------------------------------------
            # Determine final workflow state
            # ---------------------------------------

            result["workflow_id"] = workflow_id

            if result.get("awaiting_input"):

                WorkflowService.mark_waiting_for_user(
                    workflow_id=workflow_id,
                    state=result,
                    current_node=result.get(
                        "current_node"
                    )
                )

            elif result.get("next_step") in WorkflowRunner.ACTIVE_NEXT_STEPS:

                WorkflowService.mark_in_progress(
                    workflow_id=workflow_id,
                    state=result,
                    current_node=result.get(
                        "current_node"
                    )
                )

            else:

                WorkflowService.mark_completed(
                    workflow_id=workflow_id,
                    state=result,
                    current_node=result.get(
                        "current_node"
                    )
                )

            return result

        except Exception as exc:

            # ---------------------------------------
            # Workflow failure
            # ---------------------------------------

            error_message = str(exc)

            state["last_error"] = error_message

            WorkflowService.mark_failed(
                workflow_id=workflow_id,
                state=state,
                error_message=error_message,
                current_node=state.get(
                    "current_node"
                )
            )

            print(
                "\n===== WORKFLOW ERROR ====="
            )

            print(error_message)

            traceback.print_exc()

            raise
