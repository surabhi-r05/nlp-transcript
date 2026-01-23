from llm import llm
import json
import re

PROMPT = """
You must output ONLY valid JSON.
No explanations. No text.

Return execution dependencies as a JSON array.

Format:
[
  ["task_0", "task_1"],
  ["task_0", "task_2"]
]

Rules:
- Only include true dependencies
- Do NOT connect tasks that can run in parallel
- If no dependencies exist, return []

Actions:
{actions}
"""

def extract_first_json_array(text: str):
    matches = re.findall(r"\[[\s\S]*?\]", text)
    for m in matches:
        try:
            return json.loads(m)
        except json.JSONDecodeError:
            continue
    return []

def build_dag(tasks):
    edges = []

    def is_admin(text):
        return any(k in text for k in ["meeting", "schedule"])

    def task_semantics(text):
        t = text.lower()
        if any(k in t for k in ["design", "redesign", "layout", "ux"]):
            return "DESIGN"
        if any(k in t for k in ["update", "fix", "implement", "frontend"]):
            return "BUILD"
        if any(k in t for k in ["review", "approve"]):
            return "REVIEW"
        if any(k in t for k in ["client", "inform"]):
            return "COMM"
        return "OTHER"

    semantics = {t["id"]: task_semantics(t["text"]) for t in tasks}

    for t in tasks:
        t_text = t["text"].lower()

        # -------- Relation 1: explicit temporal language --------
        if any(k in t_text for k in ["after", "once", "when", "following", "upon", "as soon as","later","subsequent","next"]):
            for other in tasks:
                if other["id"] == t["id"]:
                    continue
                name = other["text"].split()[0].lower()
                if name in t_text and not is_admin(other["text"].lower()):
                    edges.append({
                        "from": other["id"],
                        "to": t["id"],
                        "relation": "temporal_after"
                    })

        # -------- Relation 2: review aggregates build --------
        if semantics[t["id"]] == "REVIEW":
            for other in tasks:
                if semantics[other["id"]] == "BUILD":
                    edges.append({
                        "from": other["id"],
                        "to": t["id"],
                        "relation": "aggregation"
                    })

        # -------- Rule 2b: review depends on design + build when explicitly stated --------
        if semantics[t["id"]] == "REVIEW" and any(
            k in t_text for k in ["after both", "after all", "once both","when both"]
        ):
            for other in tasks:
                if semantics[other["id"]] in ["DESIGN", "BUILD"]:
                    edges.append({
                        "from": other["id"],
                        "to": t["id"],
                        "relation": "group_dependency"
                    })

        # -------- Relation 3: collective completion --------
        if any(k in t_text for k in ["once they", "after everything", "when all", "after all tasks","once all tasks","when all tasks","after all of them","at the end","when they're done"]):
            for other in tasks:
                if other["id"] != t["id"] and not is_admin(other["text"].lower()):
                    edges.append({
                        "from": other["id"],
                        "to": t["id"],
                        "relation": "group_dependency"
                    })

    # -------- Deduplicate edges --------
    seen = set()
    final_edges = []
    for e in edges:
        key = (e["from"], e["to"], e["relation"])
        if key not in seen:
            seen.add(key)
            final_edges.append(e)

    return final_edges
