import json, os
from action_extractor import extract_actions
from role_assigner import assign_roles
from dag_builder import build_dag
from email_sender import send_email

# ---------- Load transcript ----------
with open("data/transcript.txt") as f:
    lines = [l.strip() for l in f if l.strip()]

actions = extract_actions(lines)
roles = assign_roles(actions)

tasks = []
for i, (a, r) in enumerate(zip(actions, roles)):
    tasks.append({
        "id": f"task_{i}",
        "text": a["text"],
        "role": r["assignee"],
        "confidence": a["confidence"]
    })

edges = build_dag(tasks)

with open("output/workflow.json", "w") as f:
    json.dump({
        "tasks": tasks,
        "edges": edges
    }, f, indent=2)


# ---------- Load participants from Downloads ----------
downloads = os.path.join(os.path.expanduser("~"), "Downloads")
participants_path = os.path.join(downloads, "participants.json")

with open(participants_path) as f:
    participants = json.load(f)

# ---------- Resolve owner ----------
def resolve_owner(task):
    text = task["text"].lower()
    for p in participants:
        if p["name"].lower() in text:
            return p
    for p in participants:
        if p["role"] == task["role"]:
            return p
    return None

tasks_by_person = {}

for t in tasks:
    owner = resolve_owner(t)
    if not owner:
        continue

    tasks_by_person.setdefault(owner["email"], {
        "name": owner["name"],
        "email": owner["email"],
        "tasks": []
    })["tasks"].append(t)

# ---------- Email + confirmation logic ----------
for person in tasks_by_person.values():
    high = [t for t in person["tasks"] if t["confidence"] >= 0.75]
    low = [t for t in person["tasks"] if t["confidence"] < 0.75]

    if high:
        body = [
            f"Hi {person['name']},",
            "",
            "From today’s meeting, here are your action items:",
            ""
        ]

        for t in high:
            body.append(f"• {t['text']}")

        body.extend([
            "",
            "Please reply if anything looks incorrect."
        ])

        send_email(
            person["email"],
            "Your action items from today’s meeting",
            "\n".join(body)
        )

    for t in low:
        print(f"❓ Needs confirmation before sending: {t['text']} → {person['name']}")

# ---------- Save workflow ----------
with open("output/workflow.json", "w") as f:
    json.dump({"tasks": tasks, "edges": edges}, f, indent=2)

print("✅ Workflow generated and emails processed")
