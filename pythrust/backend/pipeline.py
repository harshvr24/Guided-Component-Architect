from __future__ import annotations

import re
from typing import List

from pythrust.backend.contracts import GeneratePageResponse, PagePlan, RoutePlan, SectionPlan
from pythrust.backend.emitter import emit_project
from pythrust.backend.generator import generate_page_plan
from pythrust.backend.project_validator import validate_manifest


class FullPagePipeline:
    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts

    def run(self, prompt: str) -> GeneratePageResponse:
        last_error = ""

        for attempt in range(1, self.max_attempts + 1):
            generation_prompt = self._build_generation_prompt(prompt, last_error, attempt)
            raw_plan = generate_page_plan(generation_prompt)
            plan = self._normalize_plan(raw_plan, prompt)
            manifest = emit_project(plan)
            validation = validate_manifest(manifest, prompt=prompt)
            if validation.valid:
                return GeneratePageResponse(
                    status="success",
                    attempts=attempt,
                    plan=plan,
                    manifest=manifest,
                    validation=validation,
                )
            last_error = "; ".join(issue.message for issue in validation.issues if issue.level == "error") or "Validation failed"

        safe_plan = self._fallback_plan(prompt)
        safe_manifest = emit_project(safe_plan)
        safe_validation = validate_manifest(safe_manifest, prompt=prompt)
        if safe_validation.valid:
            return GeneratePageResponse(
                status="success",
                attempts=self.max_attempts,
                plan=safe_plan,
                manifest=safe_manifest,
                validation=safe_validation,
            )

        return GeneratePageResponse(
            status="failed",
            attempts=self.max_attempts,
            error=last_error or "Validation failed",
        )

    def _build_generation_prompt(self, prompt: str, last_error: str, attempt: int) -> str:
        if attempt == 1:
            return prompt

        hint = (
            "Return a valid PagePlan with non-empty pages and routes. "
            "Include semantic section children that match user intent, such as "
            "hero, features, pricing, testimonials, cta, and footer when requested."
        )
        if not last_error:
            return f"{prompt}\n{hint}"

        return (
            f"{prompt}\n"
            "Fix previous validation errors and regenerate the full plan.\n"
            f"Validation errors: {last_error}\n"
            f"{hint}"
        )

    def _normalize_plan(self, plan: PagePlan, prompt: str) -> PagePlan:
        prompt_children = self._derive_children_from_prompt(prompt)
        pages: List[SectionPlan] = []
        for i, page in enumerate(plan.pages or []):
            page_id = self._slug(page.id or page.name or f"page-{i+1}")
            name = (page.name or "Page").strip() or "Page"
            description = (page.description or prompt).strip() or prompt
            raw_children = [self._slug(c) for c in page.children if c and self._slug(c)]
            children = self._merge_children(raw_children, prompt_children)
            pages.append(
                SectionPlan(
                    id=page_id,
                    name=name,
                    description=description,
                    children=children,
                )
            )

        if not pages:
            return self._fallback_plan(prompt)

        page_ids = {p.id for p in pages}
        routes: List[RoutePlan] = []
        for route in plan.routes or []:
            clean_path = self._clean_path(route.path)
            if route.page_id in page_ids:
                routes.append(RoutePlan(path=clean_path, page_id=route.page_id))

        if not routes:
            routes = [RoutePlan(path="/", page_id=pages[0].id)]

        if not any(r.path == "/" for r in routes):
            routes.insert(0, RoutePlan(path="/", page_id=pages[0].id))

        app_name = (plan.app_name or "generated-app").strip() or "generated-app"

        return PagePlan(
            app_name=self._slug(app_name),
            pages=pages,
            routes=routes,
            design_token_version=plan.design_token_version or "v1",
        )

    def _fallback_plan(self, prompt: str) -> PagePlan:
        return PagePlan(
            app_name="generated-app",
            pages=[
                SectionPlan(
                    id="home",
                    name="Home",
                    description=prompt.strip() or "Generated page",
                    children=self._derive_children_from_prompt(prompt),
                )
            ],
            routes=[RoutePlan(path="/", page_id="home")],
            design_token_version="v1",
        )

    def _slug(self, value: str) -> str:
        value = (value or "").strip().lower()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        value = re.sub(r"-+", "-", value).strip("-")
        return value or "item"

    def _clean_path(self, path: str) -> str:
        path = (path or "/").strip()
        if not path.startswith("/"):
            path = "/" + path
        path = re.sub(r"/+", "/", path)
        return path

    def _merge_children(self, base: List[str], prompt_children: List[str]) -> List[str]:
        merged: List[str] = []
        seen: set[str] = set()

        for child in [*base, *prompt_children]:
            slug = self._slug(child)
            if slug and slug not in seen:
                seen.add(slug)
                merged.append(slug)

        if not merged:
            return ["hero", "features", "cta", "footer"]

        if "footer" not in seen:
            merged.append("footer")

        return merged

    def _derive_children_from_prompt(self, prompt: str) -> List[str]:
        text = (prompt or "").lower()
        keyword_map = {
            "hero": ["hero", "banner", "masthead"],
            "features": ["feature", "features", "benefits", "capabilities"],
            "pricing": ["pricing", "price", "plan", "plans"],
            "testimonials": ["testimonial", "testimonials", "review", "reviews"],
            "faq": ["faq", "questions"],
            "about": ["about", "story"],
            "contact": ["contact", "support"],
            "cta": ["cta", "call to action", "get started"],
            "footer": ["footer"],
        }

        ordered = ["hero", "features", "pricing", "testimonials", "faq", "about", "contact", "cta", "footer"]
        derived: List[str] = []
        for section in ordered:
            if any(re.search(rf"\b{re.escape(keyword)}\b", text) for keyword in keyword_map[section]):
                derived.append(section)

        if re.search(r"\b(landing page|marketing page|homepage|home page)\b", text):
            for section in ["hero", "features", "cta", "footer"]:
                if section not in derived:
                    derived.append(section)

        if not derived:
            return ["header", "main", "footer"]

        if "footer" not in derived:
            derived.append("footer")

        return derived
