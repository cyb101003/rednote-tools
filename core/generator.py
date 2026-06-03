import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from agents.prompts import AGENT_A_PROMPT, AGENT_B_PROMPT, AGENT_C_PROMPT
from core.social_trends import build_social_trend_context
from openai import OpenAI

load_dotenv(override=True, encoding="utf-8-sig")

# ========== 全局复用客户端 ==========
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY") or "missing-key",
    base_url=os.getenv("OPENAI_BASE_URL")
)

chroma_client = PersistentClient(path=os.getenv("CHROMA_PATH", "./data/chroma_store"))
ef = embedding_functions.DefaultEmbeddingFunction()

# ========== Few-shot 真人文案样本库 ==========
FEW_SHOT_SAMPLES = """
【真人文案风格参考 - 请模仿以下笔记的自然口吻、排版节奏和 emoji 使用习惯，但内容必须原创】

笔记1（知识干货类）：
别盲目选留学地，先看看自家收入账单📄
宝子们，留学看似是一场追逐梦想的远航，可背后家庭👨‍👩‍👦收入起着至关重要的作用！
今天小编就整理出了不同阶段收入的家庭适合去哪个国家留学～
🎄富裕家庭🎄 年入100w➕ → 🇺🇸美国 25-52w 🇬🇧英国 20-49w
🎄中产家庭🎄 年入60w➕ → 🇸🇬新加坡 20-35w 🇳🇱荷兰 15-25w
🎄小康家庭🎄 年入30w➕ → 🇪🇸西班牙 17-24w 🇯🇵日本 10-15w
🎄普通家庭🎄 年入15w➕ → 🇩🇪德国 8-10w 🇫🇷法国 5-10w
家庭收入确实在很大程度上决定了我们留学国家的选择☃

笔记2（产品推荐类）：
说实话，迄今它仍是抗老界的天花板
作为专业护肤博主我想告诉大家，不是油皮更耐老，而是让油皮显老的关键从不是那几条纹路
毛孔粗大的显形本质才是油性肤质的衰老问题，脸蛋的含水量骤降后，不仅会导致肌肤水油失衡，毛孔周围的肌肤还会失去支撑力，自然就粗大显糙，视觉年龄直线飙升！
之所以这么厉害，关键还得归功于整瓶精华里那高达90%以上的高能活性抗老成分PITERA™，它跟皮肤的天然保湿因子结构很相似，所以可以迅速渗透进肌底
我用一周多的时间，皮肤质感从内而外都提升了不少，出油量明显减少了，肤感变得清爽许多，素颜拍照整个人都更自信了，这次总算是被我get到妈生好皮的快乐！
真心建议姐妹们试试！

笔记3（个人经历吐槽类）：
真的干不动了家人们 留下来的人给到一个夯
字节的人才密度太高了，感觉日常像在和一群唐晶、贺函、钮祜禄甄嬛、还有穿prada的Miranda在协作、在竞争
人都是很优秀的人，但是事情却不一定都是有意义的事情，所以能不能收获成就感嘛就要看看运气了
不管怎么说，站在这样一艘巨轮上总是能够看到一些很美的风景、蹭到一些光芒，想要打破惯性、跳下巨轮需要很大的勇气
感谢字节、江湖再见~

笔记4（生活日常 plog 类）：
plog：好好生活 宅宅幸福
最近在慢慢布置我的新小家🎀 看着一切都变得越来越来可爱 幸福感满满🙊
发现在美团闪购买东西又快又划算！好多我经常回购的好物都有大额补贴🫶🏽
大家也要好好生活 好好爱自己哦 买东西能提供情绪价值 让自己开心就值得 在能力范围内实现自己的小愿望💫
"""

# ========== 同步参考检索 ==========
CHINESE_PLATFORMS = {"xiaohongshu", "zhihu", "weibo"}
ENGLISH_PLATFORMS = {"x", "twitter", "linkedin", "instagram", "tiktok"}


def normalize_platform(platform: str) -> str:
    return (platform or "xiaohongshu").strip().lower()


def build_language_directive(platform: str) -> str:
    platform_key = normalize_platform(platform)
    if platform_key in CHINESE_PLATFORMS:
        return (
            "Output language: Simplified Chinese.\n"
            "Do not write the final copy in English unless the user topic itself requires a short English phrase.\n"
            "Keep the voice natural for Chinese social platforms: concrete, conversational, and not like official marketing copy."
        )
    if platform_key in ENGLISH_PLATFORMS:
        return (
            "Output language: English.\n"
            "Write like a real editor or creator, not like generic AI marketing copy.\n"
            "Use natural contractions, specific lived-in details, and varied sentence lengths.\n"
            "Avoid template phrases such as 'In today's fast-paced world', 'game-changer', 'unlock', 'elevate', "
            "'delve into', 'seamless', 'transform your', 'comprehensive guide', and 'as an AI'.\n"
            "Do not include Chinese filler words or Chinese hashtags."
        )
    return (
        "Output language: English by default.\n"
        "Keep the copy conversational, specific, and platform-native."
    )


ENGLISH_FEW_SHOT_SAMPLES = """
[Real English creator style references]
Use these only as rhythm references. Do not copy exact sentences.

Post 1:
I used to think the hard part was finding better tools.
It wasn't.
The hard part was noticing where my workflow was already leaking attention.

Tiny fix that helped this week:
I stopped opening five tabs before writing the first sentence.
One doc. One messy outline. Ten minutes before touching anything else.

Not dramatic. Annoyingly effective.

Post 2:
Quick note for anyone building in public:
People don't need the polished founder version every day.
Sometimes the useful post is just:
- what broke
- what you tried
- what you learned
- what you'd do differently tomorrow

That's the stuff people actually save.

Post 3:
This is one of those small creator habits that sounds too basic until you try it:
write the caption first, then make the asset.

It forces you to know the point before you decorate it.
Cleaner post. Less wandering. Better hook.
"""


def get_references_sync(topic: str, platform: str, k: int = 3) -> str:
    refs = []
    try:
        collection = chroma_client.get_collection("hot_content")
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

# ========== LLM 调用 ==========
def call_llm_sync(prompt: str, temperature: float = 0.95) -> str:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response.choices[0].message.content.strip()

# ========== 并行生成 ==========
def build_style_reference_context(style_refs: list[str] | None) -> str:
    clean_refs = []
    for ref in style_refs or []:
        ref = str(ref).strip()
        if ref:
            clean_refs.append(ref[:1200])
    if not clean_refs:
        return ""

    joined = "\n\n".join(
        f"Reference {idx + 1}:\n{text}" for idx, text in enumerate(clean_refs[:5])
    )
    return (
        "\n\n[User-provided creator style references]\n"
        "Extract cadence, punctuation, hooks, slang, paragraph rhythm, and taboo AI-like wording. "
        "Do not copy private facts or exact sentences; create original copy in the same style.\n"
        f"{joined}"
    )


async def generate_variants(topic: str, platform: str, style_refs: list[str] | None = None) -> dict:
    platform = normalize_platform(platform)
    loop = asyncio.get_event_loop()
    ref_future = loop.run_in_executor(None, get_references_sync, topic, platform)
    trend_future = loop.run_in_executor(None, build_social_trend_context, topic, platform)
    ref_text, trend_text = await asyncio.gather(ref_future, trend_future)
    
    # Few-shot 样本 + 向量检索参考
    combined = FEW_SHOT_SAMPLES if platform in CHINESE_PLATFORMS else ENGLISH_FEW_SHOT_SAMPLES
    if trend_text:
        combined += trend_text
    if ref_text:
        combined += f"\n\n【同平台爆款参考】：\n{ref_text}"
    combined += build_style_reference_context(style_refs)
    combined += f"\n\n[Language and voice requirements]\n{build_language_directive(platform)}"
    context = f"\n\n{combined}" if combined else ""

    prompts = {
        "A": AGENT_A_PROMPT.format(topic=topic, platform=platform) + context,
        "B": AGENT_B_PROMPT.format(topic=topic, platform=platform) + context,
        "C": AGENT_C_PROMPT.format(topic=topic, platform=platform) + context,
    }

    results = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            key: executor.submit(call_llm_sync, p, 0.98)
            for key, p in prompts.items()
        }
        for key, future in futures.items():
            results[key] = future.result()
    return results
