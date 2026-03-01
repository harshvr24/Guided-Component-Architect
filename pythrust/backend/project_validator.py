import re
from typing import Dict, List, Optional

from pythrust.backend.contracts import ProjectManifest, ValidationIssue, ValidationReport
from pythrust.backend.validator import validate_component


_PROMPT_SECTION_KEYWORDS: Dict[str, List[str]] = {
    "hero": [r"\bhero\b", r"\bbanner\b", r"\bmasthead\b"],
    "features": [r"\bfeatures?\b", r"\bbenefits?\b", r"\bcapabilities\b"],
    "pricing": [r"\bpricing\b", r"\bplans?\b", r"\bprices?\b"],
    "testimonials": [r"\btestimonials?\b", r"\breviews?\b"],
    "faq": [r"\bfaq\b", r"\bquestions?\b"],
    "about": [r"\babout\b", r"\bour story\b"],
    "contact": [r"\bcontact\b", r"\breach us\b"],
    "cta": [r"\bcta\b", r"\bcall to action\b", r"\bget started\b"],
    "footer": [r"\bfooter\b"],
}

_SECTION_MARKERS: Dict[str, List[str]] = {
    "hero": [r"<header[^>]*id=\"hero\"", r"class=\"[^\"]*hero", r"<section[^>]*id=\"hero\""],
    "features": [r"id=\"features\"", r"class=\"[^\"]*features", r">\s*Features\s*<"],
    "pricing": [r"id=\"pricing\"", r"class=\"[^\"]*pricing", r">\s*Pricing\s*<"],
    "testimonials": [r"id=\"testimonials\"", r"class=\"[^\"]*testimonials", r">\s*Testimonials\s*<"],
    "faq": [r"id=\"faq\"", r"class=\"[^\"]*faq", r">\s*FAQ\s*<"],
    "about": [r"id=\"about\"", r"class=\"[^\"]*about", r">\s*About\s*<"],
    "contact": [r"id=\"contact\"", r"class=\"[^\"]*contact", r">\s*Contact\s*<"],
    "cta": [r"id=\"cta\"", r"class=\"[^\"]*cta", r">[^<]*(Get Started|Start Building|Ready to launch)"],
    "footer": [r"<footer\b", r"id=\"footer\"", r"class=\"[^\"]*footer"],
}


def validate_manifest(manifest: ProjectManifest, prompt: Optional[str] = None) -> ValidationReport:
    issues: List[ValidationIssue] = []

    file_paths = {f.path for f in manifest.files}
    if "src/app/app.routes.ts" not in file_paths:
        issues.append(
            ValidationIssue(
                level="error",
                code="MISSING_ROUTES",
                message="Missing src/app/app.routes.ts",
            )
        )

    for file in manifest.files:
        if file.kind == "html":
            base = file.path.rsplit(".", 1)[0]
            css_path = f"{base}.css"
            ts_path = f"{base}.ts"
            css = _get_content(manifest, css_path)
            ts = _get_content(manifest, ts_path)
            result = validate_component({"html": file.content, "css": css, "ts": ts})
            for err in result.errors:
                issues.append(
                    ValidationIssue(
                        level="error",
                        code="COMPONENT_VALIDATION",
                        message=err,
                        file_path=file.path,
                    )
                )
            for warn in result.warnings:
                issues.append(
                    ValidationIssue(
                        level="warning",
                        code="COMPONENT_VALIDATION_WARNING",
                        message=warn,
                        file_path=file.path,
                    )
                )

        if file.kind == "ts" and "routes" in file.path:
            route_targets = re.findall(r"component:\s*(\w+)", file.content)
            for target in route_targets:
                if target not in _component_symbols(manifest):
                    issues.append(
                        ValidationIssue(
                            level="error",
                            code="BROKEN_ROUTE_COMPONENT",
                            message=f"Route references missing component symbol {target}",
                            file_path=file.path,
                        )
                    )

    if prompt:
        _validate_prompt_alignment(manifest, prompt, issues)

    valid = not any(i.level == "error" for i in issues)
    return ValidationReport(valid=valid, issues=issues)


def _get_content(manifest: ProjectManifest, path: str) -> str:
    for file in manifest.files:
        if file.path == path:
            return file.content
    return ""


def _component_symbols(manifest: ProjectManifest) -> set[str]:
    symbols = set()
    for file in manifest.files:
        if file.kind != "ts":
            continue
        matches = re.findall(r"export\s+class\s+(\w+)", file.content)
        symbols.update(matches)
    return symbols


def _validate_prompt_alignment(manifest: ProjectManifest, prompt: str, issues: List[ValidationIssue]) -> None:
    html_files = [file for file in manifest.files if file.kind == "html"]
    if not html_files:
        issues.append(
            ValidationIssue(
                level="error",
                code="MISSING_HTML",
                message="No HTML files were generated for preview.",
            )
        )
        return

    html_blob = "\n".join(file.content for file in html_files).lower()
    text_blob = re.sub(r"<[^>]+>", " ", html_blob)
    normalized_text = _normalize_text(text_blob)
    normalized_prompt = _normalize_text(prompt)
    semantic_blocks = len(re.findall(r"<(main|header|section|article|footer|nav)\b", html_blob))

    if normalized_prompt and normalized_prompt in normalized_text and semantic_blocks < 4:
        issues.append(
            ValidationIssue(
                level="error",
                code="PROMPT_ECHO_OUTPUT",
                message="Generated preview mirrors the prompt text instead of rendering structured page sections.",
            )
        )

    expected_sections = _expected_sections(prompt)
    for section in expected_sections:
        markers = _SECTION_MARKERS.get(section, [])
        if not any(re.search(marker, html_blob, flags=re.IGNORECASE) for marker in markers):
            issues.append(
                ValidationIssue(
                    level="error",
                    code="PROMPT_SECTION_MISSING",
                    message=f"Expected '{section}' section from prompt but it was not present in generated HTML.",
                )
            )

    if len(expected_sections) >= 3 and semantic_blocks < 4:
        issues.append(
            ValidationIssue(
                level="error",
                code="INSUFFICIENT_LAYOUT_STRUCTURE",
                message="Generated HTML does not contain enough semantic layout sections for a full-page result.",
            )
        )


def _expected_sections(prompt: str) -> set[str]:
    text = (prompt or "").lower()
    expected: set[str] = set()
    for section, patterns in _PROMPT_SECTION_KEYWORDS.items():
        if any(re.search(pattern, text) for pattern in patterns):
            expected.add(section)

    if re.search(r"\b(landing page|marketing page|homepage|home page)\b", text):
        expected.update({"hero", "features", "cta", "footer"})

    return expected


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (value or "").lower())).strip()
