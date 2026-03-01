from pydantic import BaseModel, Field, field_validator
from typing import Any


class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=3)


class ComponentSchema(BaseModel):
    html: str = Field(..., min_length=1)
    css: str = Field(..., min_length=1)
    ts: str

    # -----------------------------
    # Enforce Non-Empty Strings
    # -----------------------------
    @field_validator("html", "css", "ts")
    @classmethod
    def must_be_string(cls, value: Any):
        if not isinstance(value, str):
            raise ValueError("All component fields must be strings.")
        return value

    @field_validator("html", "css")
    @classmethod
    def must_not_be_empty(cls, value: str):
        if not value.strip():
            raise ValueError("html and css cannot be empty.")
        return value