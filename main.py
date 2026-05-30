from fastapi import FastAPI
from pydantic import BaseModel
from core.generator import generate_variants
from core.judge import judge_and_select

app = FastAPI(title="RealSkill - 真人化文案引擎")

class GenerateReq(BaseModel):
    topic: str
    platform: str
    style_refs: list = []

@app.post("/generate")
async def generate(req: GenerateReq):
    variants = await generate_variants(req.topic, req.platform)
    verdict = judge_and_select(variants, req.platform)
    return {
        "variants": variants,
        "judge_result": verdict
    }
