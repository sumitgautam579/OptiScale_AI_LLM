"""
Basic smoke test for the OptiScale AI LLM agent.

This verifies that:
- The root_agent is importable.
- A simple query produces at least one final response event.
"""

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from optiscale_agent.agent import root_agent
from optiscale_agent.config import APP_NAME, DEFAULT_USER_ID, DEFAULT_SESSION_ID


def test_agent_basic_interaction():
    session_service = InMemorySessionService()

    # In ADK Python, create_session is async; Runner.run handles it internally
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # Simple question without tools, just to ensure LLM path works.
    content = types.Content(
        role="user",
        parts=[types.Part(text="Give me a high-level strategy to reduce cloud costs.")],
    )

    events = list(
        runner.run(
            user_id=DEFAULT_USER_ID,
            session_id=DEFAULT_SESSION_ID,
            new_message=content,
        )
    )

    assert any(event.is_final_response() for event in events)
