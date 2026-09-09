from backend.core.database import supabase


class AuditRepository:

    @staticmethod
    def create_event(
        workflow_id: str | None,
        agent_name: str | None,
        tool_name: str | None,
        action: str,
        status: str,
        metadata: dict | None = None,
    ):
        payload = {
            "workflow_id": workflow_id,
            "agent_name": agent_name,
            "tool_name": tool_name,
            "action": action,
            "status": status,
            "metadata": metadata or {},
        }

        response = (
            supabase.table("audit_events")
            .insert(payload)
            .execute()
        )

        return response.data
