import json
import os
from typing import Optional

from groq import Groq

from pythrust.backend.contracts import PagePlan
from pythrust.backend.design_system import load_design_tokens

SYSTEM_PROMPT_COMPONENT = """
You are a professional Angular UI generator.
Return ONLY valid JSON object with keys: html, css, ts.
No markdown, no explanations.
Use class-based styles only and no inline style attributes.
"""

SYSTEM_PROMPT_PLANNER = """
You are a software planner.
Return ONLY valid JSON matching:
{
  "app_name": "string",
  "pages": [{"id":"string","name":"string","description":"string","children":["string"]}],
  "routes": [{"path":"string","page_id":"string"}],
  "design_token_version":"string"
}
"""


class LLMGateway:
    def __init__(self):
        self._client: Optional[Groq] = None

    def _get_client(self) -> Groq:
        if self._client is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise RuntimeError("GROQ_API_KEY not configured")
            self._client = Groq(api_key=api_key)
        return self._client

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        client = self._get_client()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content


_gateway = LLMGateway()


def _strip_fences(raw_output: str) -> str:
    cleaned = raw_output.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    return cleaned.strip()


def generate_component(prompt: str) -> str:
    return _gateway.chat(SYSTEM_PROMPT_COMPONENT, prompt, temperature=0.2)


def generate_page_plan(prompt: str) -> PagePlan:
    tokens = json.dumps(load_design_tokens(), indent=2)
    try:
        raw = _gateway.chat(
            SYSTEM_PROMPT_PLANNER,
            f"Design tokens:\n{tokens}\n\nUser request:\n{prompt}",
            temperature=0.1,
        )
        cleaned = _strip_fences(raw)
        return PagePlan.model_validate(json.loads(cleaned))
    except Exception:
        return PagePlan(
            app_name="generated-app",
            pages=[
                {
                    "id": "home",
                    "name": "Home",
                    "description": prompt,
                    "children": ["header", "main", "footer"],
                }
            ],
            routes=[{"path": "/", "page_id": "home"}],
            design_token_version="v1",
        )
