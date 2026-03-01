from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pythrust.backend.contracts import GeneratePageResponse, PromptRequest
from pythrust.backend.pipeline import FullPagePipeline

app = FastAPI(title="Guided Component Architect API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = FullPagePipeline(max_attempts=3)


@app.post("/v1/generate/page", response_model=GeneratePageResponse)
def generate_page(req: PromptRequest):
    result = pipeline.run(req.prompt)
    if result.status == "failed":
        raise HTTPException(status_code=422, detail=result.error)
    return result


@app.post("/generate")
def generate_legacy(req: PromptRequest):
    result = pipeline.run(req.prompt)
    if result.status == "failed" or not result.manifest:
        return {"html": "", "css": "", "ts": "", "error": {"message": result.error or "Generation failed"}}

    html_file = next((f for f in result.manifest.files if f.path.endswith(".component.html")), None)
    css_file = next((f for f in result.manifest.files if f.path.endswith(".component.css")), None)
    ts_file = next((f for f in result.manifest.files if f.path.endswith(".component.ts")), None)

    return {
        "html": html_file.content if html_file else "",
        "css": css_file.content if css_file else "",
        "ts": ts_file.content if ts_file else "",
        "manifest": result.manifest.model_dump(),
    }
