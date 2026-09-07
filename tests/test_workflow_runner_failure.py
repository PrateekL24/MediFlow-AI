import pytest

from backend.workflows.runner import WorkflowRunner


def test_workflow_runner_marks_workflow_failed(monkeypatch):
    captured = {}

    def fake_mark_in_progress(**kwargs):
        captured["in_progress"] = kwargs

    def fake_mark_failed(**kwargs):
        captured["failed"] = kwargs

    def fake_invoke(state):
        state["current_node"] = "appointment"

        raise Exception("TEST_APPOINTMENT_FAILURE")

    monkeypatch.setattr(
        "backend.workflows.runner.WorkflowService.mark_in_progress",
        fake_mark_in_progress
    )

    monkeypatch.setattr(
        "backend.workflows.runner.WorkflowService.mark_failed",
        fake_mark_failed
    )

    monkeypatch.setattr(
        "backend.workflows.runner.graph.invoke",
        fake_invoke
    )

    with pytest.raises(Exception, match="TEST_APPOINTMENT_FAILURE"):
        WorkflowRunner.run(
            user_input="test failure",
            session_id="test-session"
        )

    assert "failed" in captured

    assert (
        captured["failed"]["error_message"]
        == "TEST_APPOINTMENT_FAILURE"
    )

    assert (
        captured["failed"]["current_node"]
        == "appointment"
    )