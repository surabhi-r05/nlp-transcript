from llm import llm
import json, re

PROMPT = """
You are assigning a SEMANTIC ROLE to each action item.

The PERSON NAME in the action text is the owner.
Your task is to label the TYPE OF WORK.

Allowed roles:
- UX Designer
- Frontend Engineer
- Backend Engineer
- QA Lead
- Project Manager

Guidelines:
- Design, navigation, layout → UX Designer
- UI, components, responsiveness → Frontend Engineer
- API, backend logic → Backend Engineer
- Testing, validation → QA Lead
- Reviews, client communication, meetings → Project Manager

Do NOT use ordering words like "after" or "once" to infer roles.

OUTPUT (JSON ONLY):
[
  {{
    "action": "<exact action text>",
    "assignee": "<role>"
  }}
]

Actions:
{actions}
"""

def assign_roles(actions):
    response = llm.invoke(PROMPT.format(actions=[a["text"] for a in actions]))

    try:
        match = re.search(r"\[.*\]", response, re.DOTALL)
        roles = json.loads(match.group())
    except:
        roles = [{"action": a["text"], "assignee": "Project Manager"} for a in actions]

    return roles
