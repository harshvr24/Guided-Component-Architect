import json
from typing import Dict, Any, List

from pythrust.backend.generator import generate_component
from pythrust.backend.validator import validate_component
from pythrust.backend.audit import log_attempt


class ComponentAgent:
    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts

    def run(self, prompt: str) -> Dict[str, Any]:
        last_errors: List[str] = []
        previous_output: str = ""
        total_attempts = 0

        for attempt in range(1, self.max_attempts + 1):
            total_attempts += 1

            print(f"[Agent] Attempt {attempt}")

            if attempt == 1:
                raw_output = generate_component(prompt)
            else:
                correction_prompt = self._build_correction_prompt(
                    prompt, previous_output, last_errors
                )
                raw_output = generate_component(correction_prompt)

            previous_output = raw_output

            try:
                structured_output = self._parse_output(raw_output)
            except Exception as e:
                last_errors = [f"[CRITICAL] Invalid JSON structure: {str(e)}"]
                continue

            validation = validate_component(structured_output)

            if validation.is_valid:
                log_attempt({
                    "prompt": prompt,
                    "attempts": total_attempts,
                    "status": "success",
                    "errors": validation.errors,
                    "warnings": validation.warnings,
                })
                return structured_output

            last_errors = validation.errors

        # Governance Blocked
        log_attempt({
            "prompt": prompt,
            "attempts": total_attempts,
            "status": "blocked",
            "errors": last_errors,
        })

        return {
            "html": "",
            "css": "",
            "ts": "",
            "error": {
                "message": "Generation blocked due to governance violations.",
                "details": last_errors,
            }
        }

    def _parse_output(self, raw_output: str) -> Dict[str, Any]:
        cleaned = raw_output.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1].strip()
        return json.loads(cleaned)

    def _build_correction_prompt(
        self,
        prompt: str,
        previous_output: str,
        errors: List[str],
    ) -> str:

        error_block = "\n".join(errors)

        return f"""
Previous output violated governance rules.

Original request:
{prompt}

Previous output:
{previous_output}

Errors:
{error_block}

Fix strictly.
Return ONLY valid JSON.
No markdown.
No explanation.
"""