import os
from dotenv import load_dotenv
from chromadb import PersistentClient
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from agents.prompts import AGENT_A_PROMPT, AGENT_B_PROMPT, AGENT_C_PROMPT
from collectors.xiaohongshu import search_xhs
from openai import OpenAI

load_dotenv(override=True)

# 初始化DeepSeek全局客户端
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

# 全局DeepSeek向量嵌入类
class DeepSeekEmbeddingFunc(EmbeddingFunction):
    def __call__(self, texts: Documents) -> Embeddings:
        resp = client.embeddings.create(input=texts, model="deepseek-embedding")
        return [item.embedding for item in resp.data]

async def get_references(topic: str, platform: str, k: int = 3) -> str:
    refs = []
    # 1. 实时采集小红书素材，增加await
    if platform == "xiaohongshu":
        try:
            notes = await search_xhs(topic, k)
            refs.extend([n["content"] for n in notes])
        except Exception:
            pass

    # 2. 向量库检索参考文案
    try:
        chroma_client = PersistentClient(path="./chroma_db")
        collection = chroma_client.get_collection("hot_content")
        ef = DeepSeekEmbeddingFunc()
        results = collection.query(
            query_texts=[topic],
            n_results=k,
            where={"platform": platform}
        )
        docs = results["documents"][0] if results["documents"] else []
        refs.extend(docs)
    except Exception as e:
        print(f"⚠️ 向量检索失败: {e}")

    unique_refs = list(dict.fromkeys(refs))[:k]
    return "\n\n".join(unique_refs)

def call_llm(prompt: str, temperature: float = 0.95) -> str:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response.choices[0].message.content.strip()

async def generate_variants(topic: str, platform: str) -> dict:
    ref_text = await get_references(topic, platform)
    context = f"\n\n【参考同平台爆款风格，禁止抄袭，仅借鉴结构口吻】：\n{ref_text}" if ref_text else ""

    prompts = {
        "A": AGENT_A_PROMPT.format(topic=topic) + context,
        "B": AGENT_B_PROMPT.format(topic=topic) + context,
        "C": AGENT_C_PROMPT.format(topic=topic) + context,
    }

    results = {}
    for key, p in prompts.items():
        results[key] = call_llm(p, temperature=0.98)
    return results
