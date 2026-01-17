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

    for i, t in enumerate(tasks):
        text = t["text"].lower()

        if "after" in text or "once" in text:
            if i > 0:
                edges.append([f"task_{i-1}", f"task_{i}"])

    return edges
