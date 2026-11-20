PROMPT = """You turn a yard worker's spoken instruction into JSON.
Fields:
- action: "move", "park", "release" or "status", or null if unclear.
- unit: the trailer number as 4 digits (write numbers said in words as digits), or null.
- to: where it goes: "door_01" to "door_08" or "staging" for move, always "parking" for park, null for release and status or if no place was said.
If the worker corrects themselves, use the last thing they said.
Instruction: {text}"""


def build_prompt(text: str) -> str:
    return PROMPT.format(text=text)
