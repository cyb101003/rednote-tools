import os
import time

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv(override=True, encoding="utf-8-sig")

from core.generator import generate_variants
from core.judge import judge_and_select, detect_ai_score
from core.humanize import humanize_by_llm, rule_based_humanize
from core.publish_cleaner import clean_publish_text, clean_variant_map
from skill_manifest import SKILL_DEFINITION

app = FastAPI(title="RealSkill - Humanized Copy Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_config_status():
    required = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL"),
    }
    missing = [key for key, value in required.items() if not value]
    ready = len(missing) == 0
    return {
        "ready": ready,
        "missing": missing,
        "message": (
            "Generation is configured and ready."
            if ready
            else "Generation is not configured on this server yet. Add OPENAI_API_KEY to .env and restart uvicorn."
        ),
    }

def use_final_llm_humanize():
    return os.getenv("FINAL_LLM_HUMANIZE", "false").strip().lower() in {"1", "true", "yes", "on"}

class SkillRequest(BaseModel):
    topic: str
    platform: str
    style_refs: list = []

@app.post("/generate")
async def generate(req: SkillRequest):
    config = get_config_status()
    if not config["ready"]:
        raise HTTPException(
            status_code=503,
            detail=config["message"],
        )
    variants = clean_variant_map(await generate_variants(req.topic, req.platform, req.style_refs))
    verdict = judge_and_select(variants, req.platform)
    winner_key = verdict.get("winner", "B")
    best_text = variants.get(winner_key) or variants.get("B") or next(iter(variants.values()))
    humanized = humanize_by_llm(best_text, req.platform) if use_final_llm_humanize() else best_text
    final = clean_publish_text(rule_based_humanize(humanized, req.platform))
    final_ai_score = detect_ai_score(final)
    risk_label = "low" if final_ai_score > 7 else "medium" if final_ai_score > 4 else "high"
    return {
        "result": final,
        "winner_agent": winner_key,
        "all_variants": variants,
        "scores": verdict.get("scores", {}),
        "judge_reason": verdict.get("reason", ""),
        "merge_strategy": verdict.get("merge_strategy", ""),
        "strengths": verdict.get("strengths", {}),
        "ai_detection_risk": risk_label,
        "ai_score": round(final_ai_score, 1),
        "humanize_mode": "llm+rules" if use_final_llm_humanize() else "rules",
        "platform": req.platform,
        "generated_at": int(time.time())
    }

@app.get("/.well-known/skill.json")
async def get_skill():
    return SKILL_DEFINITION

@app.get("/config/status")
async def config_status():
    return get_config_status()

@app.get("/health")
async def health():
    return {"status": "ok", "generation": get_config_status()}

def serve_frontend_file(filename: str):
    file_path = os.path.join(os.path.dirname(__file__), "frontend", filename)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(
                content=f.read(),
                headers={
                    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                    "Pragma": "no-cache",
                },
            )
    return HTMLResponse("<h1>RealSkill API is running</h1>")

@app.get("/app")
async def app_demo():
    return serve_frontend_file("index.html")

@app.get("/report")
async def report_page():
    return serve_frontend_file("report.html")

# ========== 代理 /app 到 Streamlit ==========
STREAMLIT_URL = "http://localhost:8501"

@app.api_route("/streamlit/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy_streamlit(path: str, request: Request):
    async with httpx.AsyncClient(base_url=STREAMLIT_URL) as client:
        url = f"/{path}"
        headers = dict(request.headers)
        headers.pop("host", None)
        body = await request.body()
        req = await client.request(
            method=request.method, url=url, headers=headers,
            content=body, params=request.query_params, timeout=30.0
        )
        response_headers = dict(req.headers)
        response_headers.pop("transfer-encoding", None)
        response_headers.pop("content-encoding", None)
        return StreamingResponse(
            req.aiter_bytes(), status_code=req.status_code,
            headers=response_headers, media_type=req.headers.get("content-type", "text/html")
        )

@app.api_route("/streamlit", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy_streamlit_root(request: Request):
    async with httpx.AsyncClient(base_url=STREAMLIT_URL) as client:
        headers = dict(request.headers)
        headers.pop("host", None)
        body = await request.body()
        req = await client.request(
            method=request.method, url="/", headers=headers,
            content=body, params=request.query_params, timeout=30.0
        )
        response_headers = dict(req.headers)
        response_headers.pop("transfer-encoding", None)
        response_headers.pop("content-encoding", None)
        return StreamingResponse(
            req.aiter_bytes(), status_code=req.status_code,
            headers=response_headers, media_type=req.headers.get("content-type", "text/html")
        )

# ========== 首页（返回 index.html）==========
@app.get("/")
async def root():
    return serve_frontend_file("landing.html")

# ========== 托管其他静态文件（CSS、JS、图片等）==========
# 注意：必须在所有 @app 路由之后，且不能用 "/" 路径
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
