from llm import llm
import re

PROMPT = """
You are given a meeting transcript.

Extract ACTION ITEMS.

An action item is a task that a participant commits to doing
after the meeting.

INSTRUCTIONS:
- Preserve the PERSON NAME in the task text.
- Phrase each action as a clear task.
- Include dates or times if mentioned.
- Ignore greetings, opinions, or discussion.
- Treat tentative language ("could", "can", "try", "maybe") as lower confidence.
- If an action depends on another, express it using natural language
  ("after", "once", "when").
  
Assign a confidence score based on commitment strength.

OUTPUT (JSON ONLY):
[
  {{
    "text": "<task>",
    "confidence": <0 to 1>
  }}
]

Transcript:
{transcript}
"""

def extract_actions(lines):
    transcript = "\n".join(lines)
    response = llm.invoke(PROMPT.format(transcript=transcript))

    actions = []
    matches = re.findall(
        r'"text"\s*:\s*"([^"]+)"\s*,\s*"confidence"\s*:\s*([0-9.]+)',
        response
    )

    for text, conf in matches:
        try:
            c = float(conf)
        except:
            c = 0.6

        actions.append({
            "text": text.strip(),
            "confidence": max(0.0, min(1.0, c))
        })

    return actions
