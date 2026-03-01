import json
from typing import Dict, Any, List

from pythrust.backend.generator import generate_component
from pythrust.backend.validator import validate_component


class ComponentAgent:
    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts

    # --------------------------------------------------

    def run(self, prompt: str) -> Dict[str, Any]:
        last_errors: List[str] = []
        previous_output: str = ""

        for attempt in range(1, self.max_attempts + 1):

            print(f"[Agent] Attempt {attempt}")

            if attempt == 1:
                raw_output = generate_component(prompt)
            else:
                correction_prompt = self._build_correction_prompt(
                    prompt=prompt,
                    previous_output=previous_output,
                    errors=last_errors,
                )
                raw_output = generate_component(correction_prompt)

            previous_output = raw_output

            try:
                structured_output = self._parse_output(raw_output)
            except Exception as e:
                last_errors = [f"Invalid JSON structure: {str(e)}"]
                print(f"[Agent] JSON parsing failed: {last_errors}")
                continue

            validation = validate_component(structured_output)

            if validation.is_valid:
                print("[Agent] Validation passed.")
                return structured_output

            last_errors = validation.errors
            print(f"[Agent] Validation failed: {last_errors}")

        print("[Agent] Generation aborted due to governance violations.")

        return {
            "html": "",
            "css": "",
            "ts": "",
            "error": {
                "message": "Generation blocked due to governance violations.",
                "details": last_errors
            }
        }

    # --------------------------------------------------

    def _parse_output(self, raw_output: str) -> Dict[str, Any]:
        cleaned = raw_output.strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1].strip()

        return json.loads(cleaned)

    # --------------------------------------------------

    def _build_correction_prompt(
        self,
        prompt: str,
        previous_output: str,
        errors: List[str],
    ) -> str:

        error_block = "\n".join(f"- {err}" for err in errors)

        return f"""
The previous output violated validation rules.

Original request:
{prompt}

Previous output:
{previous_output}

Validation errors:
{error_block}

Fix all errors strictly.
Return ONLY valid JSON.
No explanations.
No markdown.
No backticks.
Follow all architecture and governance rules.
"""