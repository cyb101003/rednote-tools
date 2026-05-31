from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from pydantic import BaseModel
from core.generator import generate_variants
from core.judge import judge_and_select, detect_ai_score
from core.humanize import humanize_by_llm, rule_based_humanize
from skill_manifest import SKILL_DEFINITION
import os
import time
import httpx

app = FastAPI(title="RealSkill - Humanized Copy Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SkillRequest(BaseModel):
    topic: str
    platform: str
    style_refs: list = []

@app.post("/generate")
async def generate(req: SkillRequest):
    variants = await generate_variants(req.topic, req.platform)
    verdict = judge_and_select(variants, req.platform)
    winner_key = verdict.get("winner", "B")
    best_text = variants[winner_key]
    humanized = humanize_by_llm(best_text)
    final = rule_based_humanize(humanized, req.platform)
    final_ai_score = detect_ai_score(final)
    risk_label = "low" if final_ai_score > 7 else "medium" if final_ai_score > 4 else "high"
    return {
        "result": final,
        "winner_agent": winner_key,
        "all_variants": variants,
        "scores": verdict.get("scores", {}),
        "ai_detection_risk": risk_label,
        "ai_score": round(final_ai_score, 1),
        "platform": req.platform,
        "generated_at": int(time.time())
    }

@app.get("/.well-known/skill.json")
async def get_skill():
    return SKILL_DEFINITION

# ========== 代理 /app 到 Streamlit ==========
STREAMLIT_URL = "http://localhost:8501"

@app.api_route("/app/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
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

@app.api_route("/app", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
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
    index_path = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"message": "RealSkill API is running"}

# ========== 托管其他静态文件（CSS、JS、图片等）==========
# 注意：必须在所有 @app 路由之后，且不能用 "/" 路径
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
