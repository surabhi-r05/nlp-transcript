import json
from action_extractor import extract_actions
from role_assigner import assign_roles
from dag_builder import build_dag
from email_sender import send_email   

# ----------------------------
# Load transcript
# ----------------------------
with open("data/transcript.txt") as f:
    lines = [l.strip() for l in f.readlines() if l.strip()]

# ----------------------------
# Extract actions + roles
# ----------------------------
actions = extract_actions(lines)
roles = assign_roles(actions)

# ----------------------------
# Build tasks
# ----------------------------
tasks = []
for i, (a, r) in enumerate(zip(actions, roles)):
    tasks.append({
        "id": f"task_{i}",
        "text": a["text"],
        "assignee": r["assignee"],   # role
        "confidence": a["confidence"]
    })

# ----------------------------
# Build DAG
# ----------------------------
edges = build_dag(tasks)

workflow = {
    "tasks": tasks,
    "edges": edges
}

with open("output/workflow.json", "w") as f:
    json.dump(workflow, f, indent=2)

print("✅ Workflow generated → output/workflow.json")

# ==========================================================
# EMAIL SENDING PART
# ==========================================================

# ----------------------------
# Load participants
# ----------------------------
try:
    with open("frontend/participants.json") as f:
        participants = json.load(f)
except FileNotFoundError:
    print("⚠️ No participants.json found — skipping email sending")
    exit(0)

# role → {name, email}
role_map = {
    p["role"]: {
        "name": p["name"],
        "email": p["email"]
    }
    for p in participants
}

# ----------------------------
# Group tasks per role
# ----------------------------
tasks_by_role = {}
for task in tasks:
    if task["confidence"] < 0.6:
        continue  # safety gate

    role = task["assignee"]
    tasks_by_role.setdefault(role, []).append(task)

# ----------------------------
# Send one email per person
# ----------------------------
for role, person_tasks in tasks_by_role.items():
    if role not in role_map:
        continue

    name = role_map[role]["name"]
    email = role_map[role]["email"]

    body_lines = [
        f"Hi {name},",
        "",
        "From today’s meeting, here are the action items assigned to you:",
        ""
    ]

    for t in person_tasks:
        body_lines.append(f"• {t['text']}")

        deps = [e["from"] for e in edges if e["to"] == t["id"]]
        if deps:
            body_lines.append(f"  ↳ Depends on: {', '.join(deps)}")


    body_lines.extend([
        "",
        "This email was auto-generated from meeting notes.",
        "Please reply if anything looks incorrect."
    ])

    body = "\n".join(body_lines)

    subject = "Your action items from today’s meeting"

    send_email(email, subject, body)

    print(f"📧 Sent tasks to {name} ({email})")

print("✅ Email dispatch complete")
