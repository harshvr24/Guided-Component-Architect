# backend/models.py

from pydantic import BaseModel, Field
from typing import Tuple


class ComponentOutput(BaseModel):
    typescript: str = Field(...)
    html: str = Field(...)
    css: str = Field(...)

    @staticmethod
    def parse_llm_output(raw: str) -> "ComponentOutput":
        """
        Strict code-only enforcement.
        Expected format:
        ---TS---
        ...
        ---HTML---
        ...
        ---CSS---
        ...
        """

        if "```" in raw:
            raw = raw.replace("```", "")

        if not all(marker in raw for marker in ["---TS---", "---HTML---", "---CSS---"]):
            raise ValueError("LLM output missing required section delimiters.")

        ts = raw.split("---TS---")[1].split("---HTML---")[0].strip()
        html = raw.split("---HTML---")[1].split("---CSS---")[0].strip()
        css = raw.split("---CSS---")[1].strip()

        return ComponentOutput(
            typescript=ts,
            html=html,
            css=css
        )


class ValidationResult(BaseModel):
    is_valid: bool
    error_type: str | None = None
    error_message: str | None = None