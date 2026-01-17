from llm import llm
import json
import re

PROMPT = """
You must output ONLY valid JSON.
Do NOT add explanations.
Do NOT use single quotes.
Do NOT omit quotes around keys.

You are assigning a ROLE responsible for each action.

Allowed roles:
- Backend Engineer
- Frontend Engineer
- UX Designer
- QA Lead
- Project Manager

Return exactly this format:
[
  {{
    "action": "<action text>",
    "assignee": "<one role from the list>"
  }}
]

Actions:
{actions}
"""

def clean_json(text: str):
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON array found")

    cleaned = match.group()
    cleaned = cleaned.replace("'", '"')
    cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)

    return json.loads(cleaned)

def assign_roles(actions):
    response = llm.invoke(
        PROMPT.format(actions=[a["text"] for a in actions])
    )

    try:
        roles = clean_json(response)
    except Exception:
        # HARD FAILSAFE
        roles = [{"action": a["text"], "assignee": "Project Manager"} for a in actions]

    # ==================================================
    # AUTHORITATIVE RULE OVERRIDES (FINAL SAY)
    # ==================================================
    for r in roles:
        t = r["action"].lower()

        # 1️⃣ Meeting / scheduling → PM
        if any(k in t for k in [
            "schedule", "create meeting", "set up meeting",
            "follow-up meeting", "regroup", "sync"
        ]):
            r["assignee"] = "Project Manager"

        # 2️⃣ QA
        elif any(k in t for k in [
            "test", "testing", "qa", "regression", "validate"
        ]):
            r["assignee"] = "QA Lead"

        # 3️⃣ Backend
        elif any(k in t for k in [
            "api", "backend", "database", "server",
            "export", "integration"
        ]):
            r["assignee"] = "Backend Engineer"

        # 4️⃣ UX / Design
        elif any(k in t for k in [
            "design", "layout", "ux", "ui", "wireframe", "redesign"
        ]):
            r["assignee"] = "UX Designer"

        # 5️⃣ Frontend
        elif any(k in t for k in [
            "frontend", "component", "ui changes", "adjust components"
        ]):
            r["assignee"] = "Frontend Engineer"

        # 6️⃣ Communication → PM
        elif any(k in t for k in [
            "client", "inform", "update", "communicate", "email"
        ]):
            r["assignee"] = "Project Manager"

        # 7️⃣ Default safety
        else:
            r["assignee"] = r.get("assignee", "Project Manager")

    return roles
