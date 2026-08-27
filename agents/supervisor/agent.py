import json
import time

from backend.core.llm import llm
from backend.workflows.state import GraphState
from .prompt import SYSTEM_PROMPT


def supervisor_agent(state: GraphState):

    user_input = state["user_input"].strip()

    context = {
        "selected_doctor": state.get(
            "selected_doctor"
        ),
        "doctors_found": state.get(
            "doctors_found"
        ) or [],
        "selected_patient": state.get(
            "selected_patient"
        )
    }

    # ---------------------------------------
    # Supervisor is ONLY for new requests.
    #
    # Follow-up inputs such as:
    # 30
    # 1
    # 9999999999
    #
    # never reach this function because the
    # graph routes them directly to the
    # appropriate agent.
    # ---------------------------------------

    prompt = f"""
{SYSTEM_PROMPT}

Context:
{json.dumps(context)}

User:
{user_input}
"""

    # ---------------------------------------
    # Gemini timing
    # ---------------------------------------

    print(
        f"\n[{time.strftime('%H:%M:%S')}] "
        "Supervisor started"
    )

    start_time = time.perf_counter()

    print(
        f"[{time.strftime('%H:%M:%S')}] "
        "Calling Gemini..."
    )

    response = llm.invoke(prompt)

    elapsed = time.perf_counter() - start_time

    print(
        f"[{time.strftime('%H:%M:%S')}] "
        f"Gemini response received | "
        f"{elapsed:.2f} sec"
    )

    # ---------------------------------------
    # Parse Gemini response
    # ---------------------------------------

    try:

        raw_text = response.content[0]["text"]

        data = json.loads(raw_text)

    except (
        json.JSONDecodeError,
        KeyError,
        TypeError,
        IndexError
    ):

        data = {
            "intent": "unknown",
            "patient_data": {},
            "request_data": {},
            "response": (
                "Sorry, I couldn't understand your request."
            )
        }

    # ---------------------------------------
    # Save Supervisor result
    # ---------------------------------------

    state["intent"] = data.get(
        "intent",
        "unknown"
    )

    state["patient_data"] = data.get(
        "patient_data",
        {}
    )

    state["request_data"] = data.get(
        "request_data",
        {}
    )

    state["response"] = data.get(
        "response",
        ""
    )

    state["current_agent"] = "Supervisor"
    state["awaiting_input"] = None

    return state
