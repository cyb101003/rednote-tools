import chromadb
from chromadb.utils import embedding_functions
from data.seed_data import XHS_SAMPLES, ZHIHU_SAMPLES, WEIBO_SAMPLES
import os

# 使用本地中文 Embedding 模型（无需 API，离线可用）
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="shibing624/text2vec-base-chinese"
)

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="hot_content",
    embedding_function=embed_fn
)

def add_samples(samples, platform):
    for item in samples:
        collection.add(
            documents=[item["content"]],
            metadatas=[{
                "platform": platform,
                "title": item["title"],
                "likes": item["likes"]
            }],
            ids=[f"{platform}_{item['title']}"]
        )

if __name__ == "__main__":
    add_samples(XHS_SAMPLES, "xiaohongshu")
    add_samples(ZHIHU_SAMPLES, "zhihu")
    add_samples(WEIBO_SAMPLES, "weibo")
    print(f"✅ Vector DB built. Total documents: {collection.count()}")
