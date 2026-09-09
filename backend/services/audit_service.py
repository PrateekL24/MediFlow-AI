from backend.repositories.audit_repository import AuditRepository


class AuditService:
    """Best-effort operational audit logging."""

    @staticmethod
    def record_event(
        workflow_id: str | None,
        agent_name: str | None,
        tool_name: str | None,
        action: str,
        status: str,
        metadata: dict | None = None,
    ):
        try:
            return AuditRepository.create_event(
                workflow_id=workflow_id,
                agent_name=agent_name,
                tool_name=tool_name,
                action=action,
                status=status,
                metadata=metadata or {},
            )
        except Exception as exc:
            print(f"Audit logging failed: {exc}")
            return None
