# backend/memory.py

from typing import List


class ConversationMemory:
    """
    Stores multi-turn prompts and provides contextual stitching.
    """

    def __init__(self):
        self.history: List[str] = []

    def add(self, prompt: str):
        self.history.append(prompt)

    def build_context(self) -> str:
        if not self.history:
            return ""
        return "\n".join(
            [f"User Instruction {i+1}: {p}" for i, p in enumerate(self.history)]
        )

    def clear(self):
        self.history = []