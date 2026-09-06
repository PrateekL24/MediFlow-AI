from typing import Optional

from backend.core.database import supabase


class WorkflowRepository:

    @staticmethod
    def create_workflow(
        workflow_id: str,
        session_id: str,
        workflow_state: dict,
        current_agent: Optional[str] = None,
        current_node: Optional[str] = None,
        status: str = "running"
    ):

        data = {
            "workflow_id": workflow_id,
            "session_id": session_id,
            "current_agent": current_agent,
            "current_node": current_node,
            "workflow_state": workflow_state,
            "status": status
        }

        response = (
            supabase
            .table("workflow_runs")
            .insert(data)
            .execute()
        )

        return response.data

    @staticmethod
    def get_workflow(workflow_id: str):

        response = (
            supabase
            .table("workflow_runs")
            .select("*")
            .eq("workflow_id", workflow_id)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    @staticmethod
    def update_workflow(
        workflow_id: str,
        workflow_state: Optional[dict] = None,
        current_agent: Optional[str] = None,
        current_node: Optional[str] = None,
        status: Optional[str] = None
    ):

        data = {}

        if workflow_state is not None:
            data["workflow_state"] = workflow_state

        # These fields are intentionally added even when
        # their value is None so the database can be cleared.
        data["current_agent"] = current_agent
        data["current_node"] = current_node

        if status is not None:
            data["status"] = status

        if not data:
            return []

        response = (
            supabase
            .table("workflow_runs")
            .update(data)
            .eq("workflow_id", workflow_id)
            .execute()
        )

        return response.data

    @staticmethod
    def update_status(
        workflow_id: str,
        status: str
    ):

        response = (
            supabase
            .table("workflow_runs")
            .update({
                "status": status
            })
            .eq("workflow_id", workflow_id)
            .execute()
        )

        return response.data