import re
from typing import Dict, List

from pythrust.backend.contracts import GeneratedFile, PagePlan, ProjectManifest, SectionPlan
from pythrust.backend.design_system import load_design_tokens


_SECTION_ORDER = [
    "hero",
    "features",
    "pricing",
    "testimonials",
    "faq",
    "about",
    "contact",
    "cta",
    "footer",
]

_SECTION_ALIASES: Dict[str, set[str]] = {
    "hero": {"hero", "banner", "masthead", "intro"},
    "features": {"feature", "features", "benefits", "capabilities"},
    "pricing": {"pricing", "plans", "plan", "price"},
    "testimonials": {"testimonial", "testimonials", "review", "reviews"},
    "faq": {"faq", "questions", "question"},
    "about": {"about", "story"},
    "contact": {"contact", "support"},
    "cta": {"cta", "call-to-action", "call-toaction", "call-to", "action"},
    "footer": {"footer"},
    "header": {"header", "nav", "navbar", "navigation"},
    "main": {"main", "content"},
}


def emit_project(plan: PagePlan) -> ProjectManifest:
    files: List[GeneratedFile] = [
        GeneratedFile(
            path="src/app/app.routes.ts",
            kind="ts",
            content=_emit_routes(plan),
        )
    ]

    for page in plan.pages:
        base = f"src/app/pages/{page.id}"
        selector = f"app-{page.id}"
        component_name = _component_name(page)
        sections = _select_sections(page)
        files.extend(
            [
                GeneratedFile(
                    path=f"{base}/{page.id}.component.ts",
                    kind="ts",
                    content=(
                        "import { Component } from '@angular/core';\n\n"
                        "@Component({\n"
                        f"  selector: '{selector}',\n"
                        f"  templateUrl: './{page.id}.component.html',\n"
                        f"  styleUrl: './{page.id}.component.css'\n"
                        "})\n"
                        f"export class {component_name} {{}}\n"
                    ),
                ),
                GeneratedFile(
                    path=f"{base}/{page.id}.component.html",
                    kind="html",
                    content=_emit_page_html(page, sections),
                ),
                GeneratedFile(
                    path=f"{base}/{page.id}.component.css",
                    kind="css",
                    content=_emit_page_css(page),
                ),
            ]
        )

    files.append(
        GeneratedFile(
            path="project-manifest.json",
            kind="json",
            content=plan.model_dump_json(indent=2),
        )
    )

    return ProjectManifest(
        app_name=plan.app_name,
        files=files,
        entrypoints={"routes": "src/app/app.routes.ts"},
    )


def _component_name(page: SectionPlan) -> str:
    base = re.sub(r"[^a-zA-Z0-9]", "", page.name or page.id or "Page")
    if not base:
        base = "Page"
    if base[0].isdigit():
        base = f"Page{base}"
    return f"{base}Component"


def _select_sections(page: SectionPlan) -> List[str]:
    selected: List[str] = []
    seen: set[str] = set()
    for raw in page.children:
        canonical = _canonical_section(raw)
        if canonical and canonical not in seen:
            seen.add(canonical)
            selected.append(canonical)

    description = (page.description or "").lower()
    for section in _SECTION_ORDER:
        if section in seen:
            continue
        aliases = _SECTION_ALIASES.get(section, {section})
        if any(re.search(rf"\b{re.escape(alias)}\b", description) for alias in aliases):
            seen.add(section)
            selected.append(section)

    if not selected:
        selected = ["hero", "features", "cta", "footer"]

    if "hero" in seen and "hero" not in selected:
        selected.insert(0, "hero")
    if "footer" not in selected:
        selected.append("footer")

    return sorted(selected, key=lambda section: _SECTION_ORDER.index(section) if section in _SECTION_ORDER else 999)


def _canonical_section(value: str) -> str | None:
    slug = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    for canonical, aliases in _SECTION_ALIASES.items():
        if slug in aliases:
            return canonical
    return slug or None


def _emit_page_html(page: SectionPlan, sections: List[str]) -> str:
    blocks: List[str] = [f"<main class=\"page page-{page.id}\">"]
    for section in sections:
        blocks.append(_section_block(section, page))
    blocks.append("</main>")
    return "\n".join(blocks) + "\n"


def _section_block(section: str, page: SectionPlan) -> str:
    page_title = page.name or "Generated Page"
    prompt_hint = (page.description or "").strip()
    short_hint = prompt_hint[:160].rstrip()
    if short_hint and not short_hint.endswith("."):
        short_hint = f"{short_hint}."

    if section == "hero":
        return (
            "  <header class=\"block block-hero\" id=\"hero\">\n"
            "    <p class=\"eyebrow\">Generated Experience</p>\n"
            f"    <h1>{page_title}</h1>\n"
            f"    <p class=\"subtitle\">{short_hint or 'A structured layout generated from your prompt.'}</p>\n"
            "    <div class=\"hero-actions\">\n"
            "      <button class=\"btn btn-primary\">Get Started</button>\n"
            "      <button class=\"btn btn-secondary\">View Details</button>\n"
            "    </div>\n"
            "  </header>"
        )

    if section == "features":
        return (
            "  <section class=\"block block-features\" id=\"features\">\n"
            "    <h2>Features</h2>\n"
            "    <div class=\"grid grid-3\">\n"
            "      <article class=\"card\"><h3>Fast Setup</h3><p>Start quickly with generated scaffolding and sensible defaults.</p></article>\n"
            "      <article class=\"card\"><h3>Design Governance</h3><p>Styles follow design tokens and validation rules.</p></article>\n"
            "      <article class=\"card\"><h3>Composable Sections</h3><p>Build pages from reusable semantic blocks.</p></article>\n"
            "    </div>\n"
            "  </section>"
        )

    if section == "pricing":
        return (
            "  <section class=\"block block-pricing\" id=\"pricing\">\n"
            "    <h2>Pricing</h2>\n"
            "    <div class=\"grid grid-3\">\n"
            "      <article class=\"card plan\"><h3>Starter</h3><p class=\"price\">$19<span>/mo</span></p><p>For small teams.</p></article>\n"
            "      <article class=\"card plan featured\"><h3>Growth</h3><p class=\"price\">$49<span>/mo</span></p><p>For scaling products.</p></article>\n"
            "      <article class=\"card plan\"><h3>Enterprise</h3><p class=\"price\">Custom</p><p>For advanced governance needs.</p></article>\n"
            "    </div>\n"
            "  </section>"
        )

    if section == "testimonials":
        return (
            "  <section class=\"block block-testimonials\" id=\"testimonials\">\n"
            "    <h2>Testimonials</h2>\n"
            "    <div class=\"grid grid-2\">\n"
            "      <blockquote class=\"card quote\">\"We shipped faster in days, not weeks.\"<cite> Product Lead</cite></blockquote>\n"
            "      <blockquote class=\"card quote\">\"Consistent quality with less manual rework.\"<cite> Engineering Manager</cite></blockquote>\n"
            "    </div>\n"
            "  </section>"
        )

    if section == "faq":
        return (
            "  <section class=\"block block-faq\" id=\"faq\">\n"
            "    <h2>FAQ</h2>\n"
            "    <div class=\"faq-list\">\n"
            "      <article class=\"card\"><h3>Can I customize this layout?</h3><p>Yes. Generated files are editable and structured for extension.</p></article>\n"
            "      <article class=\"card\"><h3>Does it enforce tokens?</h3><p>Validation checks enforce basic design-system rules.</p></article>\n"
            "    </div>\n"
            "  </section>"
        )

    if section == "about":
        return (
            "  <section class=\"block block-about\" id=\"about\">\n"
            "    <h2>About</h2>\n"
            "    <p>Built to turn high-level product prompts into governed, production-friendly scaffolds.</p>\n"
            "  </section>"
        )

    if section == "contact":
        return (
            "  <section class=\"block block-contact\" id=\"contact\">\n"
            "    <h2>Contact</h2>\n"
            "    <div class=\"card contact-card\">\n"
            "      <p>Email: hello@example.com</p>\n"
            "      <p>Phone: +1 (555) 123-4567</p>\n"
            "    </div>\n"
            "  </section>"
        )

    if section == "cta":
        return (
            "  <section class=\"block block-cta\" id=\"cta\">\n"
            "    <h2>Ready to launch?</h2>\n"
            "    <p>Use this generated scaffold as your baseline and iterate from here.</p>\n"
            "    <button class=\"btn btn-primary\">Start Building</button>\n"
            "  </section>"
        )

    if section == "footer":
        return (
            "  <footer class=\"block block-footer\" id=\"footer\">\n"
            "    <p>Built with Guided Component Architect</p>\n"
            "    <nav class=\"footer-nav\">\n"
            "      <a href=\"#hero\">Home</a>\n"
            "      <a href=\"#features\">Features</a>\n"
            "      <a href=\"#pricing\">Pricing</a>\n"
            "    </nav>\n"
            "  </footer>"
        )

    return (
        f"  <section class=\"block block-{section}\" id=\"{section}\">\n"
        f"    <h2>{section.replace('-', ' ').title()}</h2>\n"
        "  </section>"
    )


def _emit_page_css(page: SectionPlan) -> str:
    tokens = load_design_tokens()
    colors = tokens.get("colors", {})
    spacing = tokens.get("spacing", {})
    radius = tokens.get("border-radius", {})
    typography = tokens.get("typography", {})
    shadows = tokens.get("shadows", {})

    primary = colors.get("primary", "#6366f1")
    primary_hover = colors.get("primary-hover", "#4f46e5")
    secondary = colors.get("secondary", "#8b5cf6")
    surface = colors.get("surface", "#ffffff")
    background = colors.get("background", "#f8fafc")
    text = colors.get("text", "#1e293b")
    text_muted = colors.get("text-muted", "#64748b")
    border = colors.get("border", "#e2e8f0")

    gap_sm = spacing.get("sm", "8px")
    gap_md = spacing.get("md", "16px")
    gap_lg = spacing.get("lg", "24px")
    gap_xl = spacing.get("xl", "32px")
    radius_md = radius.get("md", "8px")
    radius_lg = radius.get("lg", "12px")
    font_family = typography.get("font-family", "Inter, system-ui, sans-serif")
    font_sm = typography.get("font-size-sm", "14px")
    font_md = typography.get("font-size-md", "16px")
    font_lg = typography.get("font-size-lg", "18px")
    _ = shadows  # kept to avoid changing token loading behavior

    return (
        f".page {{\n"
        f"  font-family: {font_family};\n"
        f"  color: {text};\n"
        f"  background-color: {background};\n"
        f"  padding: {gap_xl};\n"
        f"  display: grid;\n"
        f"  gap: {gap_lg};\n"
        f"}}\n\n"
        ".block {\n"
        f"  background-color: {surface};\n"
        f"  border: 1px solid {border};\n"
        f"  border-radius: {radius_lg};\n"
        f"  padding: {gap_lg};\n"
        "}\n\n"
        ".eyebrow {\n"
        f"  color: {secondary};\n"
        f"  font-size: {font_sm};\n"
        f"  font-weight: 700;\n"
        f"  margin: 0 0 {gap_sm} 0;\n"
        "}\n\n"
        ".block h1,\n"
        ".block h2,\n"
        ".block h3 {\n"
        "  margin: 0;\n"
        "}\n\n"
        ".subtitle {\n"
        f"  color: {text_muted};\n"
        f"  font-size: {font_md};\n"
        f"  margin: {gap_sm} 0 0 0;\n"
        "}\n\n"
        ".hero-actions {\n"
        f"  margin: {gap_md} 0 0 0;\n"
        "  display: grid;\n"
        "  grid-template-columns: repeat(2, minmax(0, 1fr));\n"
        f"  gap: {gap_sm};\n"
        "  align-items: center;\n"
        "}\n\n"
        ".btn {\n"
        f"  border-radius: {radius_md};\n"
        f"  padding: {gap_sm} {gap_md};\n"
        f"  border: 1px solid {border};\n"
        "  cursor: pointer;\n"
        "  font-weight: 600;\n"
        f"  font-size: {font_md};\n"
        "  text-align: center;\n"
        f"  background-color: {surface};\n"
        f"  color: {text};\n"
        "}\n\n"
        ".btn-primary {\n"
        f"  background-color: {primary};\n"
        "  color: #ffffff;\n"
        f"  border-color: {primary};\n"
        "}\n\n"
        ".btn-secondary {\n"
        f"  background-color: {surface};\n"
        f"  border-color: {border};\n"
        f"  color: {text};\n"
        "}\n\n"
        ".grid {\n"
        "  display: grid;\n"
        f"  gap: {gap_md};\n"
        "}\n\n"
        ".grid-3 {\n"
        "  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));\n"
        "}\n\n"
        ".grid-2 {\n"
        "  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));\n"
        "}\n\n"
        ".card {\n"
        f"  border: 1px solid {border};\n"
        f"  border-radius: {radius_md};\n"
        f"  padding: {gap_md};\n"
        f"  background-color: {surface};\n"
        "}\n\n"
        ".plan.featured {\n"
        f"  border-color: {primary_hover};\n"
        "}\n\n"
        ".price {\n"
        f"  font-size: {font_lg};\n"
        "  font-weight: 700;\n"
        f"  margin: {gap_sm} 0;\n"
        "}\n\n"
        ".price span {\n"
        f"  font-size: {font_sm};\n"
        f"  color: {text_muted};\n"
        "}\n\n"
        ".quote {\n"
        "  margin: 0;\n"
        "}\n\n"
        ".quote cite {\n"
        f"  margin: {gap_sm} 0 0 0;\n"
        f"  color: {text_muted};\n"
        "}\n\n"
        ".footer-nav {\n"
        "  display: grid;\n"
        "  grid-template-columns: repeat(3, minmax(0, 1fr));\n"
        f"  gap: {gap_md};\n"
        "  align-items: center;\n"
        "}\n\n"
        ".footer-nav a {\n"
        f"  color: {primary};\n"
        "  font-weight: 600;\n"
        "}\n"
    )


def _emit_routes(plan: PagePlan) -> str:
    imports = []
    route_defs = []

    for route in plan.routes:
        page = next((p for p in plan.pages if p.id == route.page_id), None)
        if not page:
            continue
        component_name = _component_name(page)
        import_path = f"./pages/{page.id}/{page.id}.component"
        imports.append(f"import {{ {component_name} }} from '{import_path}';")
        route_defs.append(f"  {{ path: '{route.path.lstrip('/')}', component: {component_name} }},")

    return "\n".join(
        [
            "import { Routes } from '@angular/router';",
            *imports,
            "",
            "export const routes: Routes = [",
            *route_defs,
            "];",
        ]
    )
