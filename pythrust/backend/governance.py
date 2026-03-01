import re
from typing import Dict, List, Tuple

from pythrust.backend.design_system import allowed_colors

POLICY_VERSION = "v2.0.0"

ALLOWED_CSS_PROPERTIES = {
    "display",
    "padding",
    "margin",
    "background",
    "background-color",
    "color",
    "border",
    "border-color",
    "border-radius",
    "font-size",
    "font-weight",
    "font-family",
    "cursor",
    "text-align",
    "width",
    "height",
    "grid-template-columns",
    "gap",
    "align-items",
    "justify-content",
}

DISALLOWED_HTML_TAGS = {"script", "iframe", "object", "embed", "link", "meta"}

MAX_HTML_LENGTH = 8000
MAX_CSS_LENGTH = 16000
MAX_CLASS_COUNT = 200


def enforce_governance(component: Dict[str, str]) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    html = component.get("html", "")
    css = component.get("css", "")

    for tag in DISALLOWED_HTML_TAGS:
        if re.search(rf"<\s*{tag}", html, re.IGNORECASE):
            errors.append(f"[CRITICAL] Disallowed HTML tag detected: <{tag}>")

    css_properties = re.findall(r"([\w-]+)\s*:", css)
    for prop in css_properties:
        if prop not in ALLOWED_CSS_PROPERTIES:
            errors.append(f"[HIGH] Disallowed CSS property used: {prop}")

    approved_colors = allowed_colors()
    color_properties = re.findall(
        r"(color|background|background-color|border-color)\s*:\s*([^;]+)",
        css,
        re.IGNORECASE,
    )

    for _, value in color_properties:
        value = value.strip()
        match = re.search(r"(#(?:[0-9a-fA-F]{3}){1,2}|\b[a-zA-Z]+\b)", value)
        if match:
            color = match.group(1).lower()
            if color not in approved_colors:
                errors.append(f"[HIGH] Non-approved color token used: {color}")

    if len(html) > MAX_HTML_LENGTH:
        warnings.append("[MEDIUM] HTML exceeds recommended length.")
    if len(css) > MAX_CSS_LENGTH:
        warnings.append("[MEDIUM] CSS exceeds recommended length.")

    classes = re.findall(r"\.(\w+)", css)
    if len(set(classes)) > MAX_CLASS_COUNT:
        warnings.append("[LOW] Large number of CSS classes defined.")

    return errors, warnings
