from __future__ import annotations

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=3)
    session_id: Optional[str] = None


class SectionPlan(BaseModel):
    id: str
    name: str
    description: str
    children: List[str] = Field(default_factory=list)


class RoutePlan(BaseModel):
    path: str
    page_id: str


class PagePlan(BaseModel):
    app_name: str
    pages: List[SectionPlan]
    routes: List[RoutePlan]
    design_token_version: str = "v1"


class GeneratedFile(BaseModel):
    path: str
    kind: Literal["ts", "html", "css", "json", "md"]
    content: str


class ProjectManifest(BaseModel):
    app_name: str
    framework: Literal["angular"] = "angular"
    files: List[GeneratedFile]
    entrypoints: Dict[str, str] = Field(default_factory=dict)


class ValidationIssue(BaseModel):
    level: Literal["error", "warning"]
    code: str
    message: str
    file_path: Optional[str] = None


class ValidationReport(BaseModel):
    valid: bool
    issues: List[ValidationIssue] = Field(default_factory=list)


class GeneratePageResponse(BaseModel):
    status: Literal["success", "failed"]
    plan: Optional[PagePlan] = None
    manifest: Optional[ProjectManifest] = None
    validation: Optional[ValidationReport] = None
    attempts: int = 0
    error: Optional[str] = None
