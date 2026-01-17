from llm import llm
import re

PROMPT = """
You are given a meeting transcript.

Extract all ACTION ITEMS. - impicilt and explicit
An action item is something someone will do after the meeting.

INCLUDE:
- Tasks someone commits to doing
- Follow-ups (emailing, updating, informing)
- Scheduling or creating meetings
- Preparing designs, code changes, testing, reviews

EXCLUDE:
- Opinions, observations, or discussion
- Ideas without commitment
- Future possibilities ("keep in mind", "maybe later")

If an action is tentative or depends on something else, still include it
but assign LOWER confidence.

Return JSON ONLY in this format:
[
  {{
    "text": "<clear action phrased as a task>",
    "confidence": <number between 0 and 1>
  }}
]

Transcript:
{transcript}
"""

def extract_actions(lines):
    transcript = "\n".join(lines)
    response = llm.invoke(PROMPT.format(transcript=transcript))

    # ---- robust manual parsing ----
    actions = []

    blocks = re.findall(
        r'"text"\s*:\s*"([^"]+)"\s*,\s*"confidence"\s*:\s*([0-9.]+)',
        response
    )

    for text, conf in blocks:
        try:
            confidence = float(conf)
        except Exception:
            confidence = 0.5

        confidence = max(0.0, min(1.0, confidence))

        actions.append({
            "text": text,
            "confidence": confidence
        })

    if not actions:
        print("⚠️ Action extraction failed, raw output below:")
        print(response)

    return actions
