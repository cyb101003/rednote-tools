import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
import random

USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S9080) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
]

async def fetch_xhs_notes(keyword: str, max_notes: int = 5) -> list[dict]:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": 390, "height": 844},
                locale="zh-CN"
            )
            page = await context.new_page()
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes"
            await page.goto(search_url, wait_until="networkidle")
            try:
                await page.wait_for_selector("section.note-item", timeout=10000)
            except:
                await browser.close()
                return []

            html = await page.content()
            soup = BeautifulSoup(html, "lxml")
            notes = []
            for item in soup.select("section.note-item")[:max_notes]:
                title_tag = item.select_one(".title")
                title = title_tag.text.strip() if title_tag else ""
                desc_tag = item.select_one(".desc")
                desc = desc_tag.text.strip() if desc_tag else title
                like_tag = item.select_one(".like-wrapper .count")
                likes = int(re.sub(r'\D', '', like_tag.text)) if like_tag else 0
                link = ""
                a_tag = item.find("a")
                if a_tag and a_tag.get("href"):
                    link = "https://www.xiaohongshu.com" + a_tag["href"]
                notes.append({
                    "title": title,
                    "content": desc,
                    "likes": likes,
                    "url": link
                })
            await browser.close()
            return notes
    except Exception:
        return []

def search_xhs(keyword: str, count=5):
    return asyncio.run(fetch_xhs_notes(keyword, count))
