import chromadb
from chromadb.utils import embedding_functions
from data.seed_data import XHS_SAMPLES, ZHIHU_SAMPLES, WEIBO_SAMPLES
import os
from dotenv import load_dotenv

load_dotenv()

# 使用 ChromaDB 自带的轻量 Embedding（完全离线，不联网）
embed_fn = embedding_functions.DefaultEmbeddingFunction()

chroma_client = chromadb.PersistentClient(path="./chroma_db")

# 删除旧集合
try:
    chroma_client.delete_collection("hot_content")
except:
    pass

collection = chroma_client.create_collection(
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
    print(f"✅ Vector DB rebuilt. Total documents: {collection.count()}")
