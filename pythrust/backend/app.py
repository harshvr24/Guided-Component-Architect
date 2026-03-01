from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import zipfile
import uuid

from pipeline import GuidedComponentArchitect

# -------------------------
# FastAPI App Setup
# -------------------------

app = FastAPI(title="Guided Component Architect API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

architect = GuidedComponentArchitect(
    design_system_path="design-system/design-tokens.json"
)

# -------------------------
# Request Schema
# -------------------------

class GenerateRequest(BaseModel):
    prompt: str


# -------------------------
# Generate Endpoint
# -------------------------

@app.post("/generate")
def generate_component(request: GenerateRequest):
    result = architect.run(request.prompt)

    if result["status"] == "failed":
        raise HTTPException(
            status_code=400,
            detail={
                "errors": result.get("errors", []),
                "attempts": result.get("attempts", 0),
            }
        )

    return {
        "status": "success",
        "attempts": result["attempts"],
        "component_ts": result["data"]["component_ts"],
        "component_html": result["data"]["component_html"],
        "component_css": result["data"]["component_css"],
    }


# -------------------------
# Export Endpoint
# -------------------------

@app.post("/export")
def export_component(request: GenerateRequest):
    result = architect.run(request.prompt)

    if result["status"] == "failed":
        raise HTTPException(
            status_code=400,
            detail={
                "errors": result.get("errors", []),
                "attempts": result.get("attempts", 0),
            }
        )

    component = result["data"]

    export_id = str(uuid.uuid4())
    export_dir = f"exports/{export_id}"
    os.makedirs(export_dir, exist_ok=True)

    ts_path = os.path.join(export_dir, "component.ts")
    html_path = os.path.join(export_dir, "component.html")
    css_path = os.path.join(export_dir, "component.css")

    with open(ts_path, "w") as f:
        f.write(component["component_ts"])

    with open(html_path, "w") as f:
        f.write(component["component_html"])

    with open(css_path, "w") as f:
        f.write(component["component_css"])

    zip_path = f"{export_dir}.zip"

    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.write(ts_path, "component.ts")
        zipf.write(html_path, "component.html")
        zipf.write(css_path, "component.css")

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="angular_component.zip"
    )