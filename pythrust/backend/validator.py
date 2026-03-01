from typing import Dict, List
import re
from pythrust.backend.governance import enforce_governance


class ValidationResult:
    def __init__(self, errors: List[str], warnings: List[str]):
        self.errors = errors
        self.warnings = warnings

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


def validate_component(component: Dict[str, str]) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []

    required_keys = ["html", "css", "ts"]

    for key in required_keys:
        if key not in component:
            errors.append(f"[CRITICAL] Missing required key: {key}")

    if errors:
        return ValidationResult(errors, warnings)

    html = component["html"]
    css = component["css"]
    ts = component["ts"]

    if not isinstance(html, str):
        errors.append("[CRITICAL] HTML must be a string.")
    if not isinstance(css, str):
        errors.append("[CRITICAL] CSS must be a string.")
    if not isinstance(ts, str):
        errors.append("[CRITICAL] TS must be a string.")

    if not html.strip():
        errors.append("[CRITICAL] HTML cannot be empty.")
    if not css.strip():
        errors.append("[CRITICAL] CSS cannot be empty.")

    if re.search(r'style\s*=', html):
        errors.append("[HIGH] Inline styles are not allowed in HTML.")

    if "class=" not in html:
        errors.append("[HIGH] HTML must use CSS classes.")

    governance_errors, governance_warnings = enforce_governance(component)

    errors.extend(governance_errors)
    warnings.extend(governance_warnings)

    return ValidationResult(errors, warnings)