import asyncio
import aiohttp
from urllib.parse import quote
from ddgs import DDGS
from core.parser import clean_scraped_text
import re

# Helper to clean DDG web snippets
def clean_ddg_text(results: list) -> list[str]:
    sentences = []
    for res in results:
        body = res.get("body", "").strip()
        if body:
            # Clean up trailing ellipses from search snippets
            body = re.sub(r'\.\.\.$', '', body)
            sentences.append(body)
    return sentences[:3] # Return top 3 cleanest snippets

async def fetch_text_data(session: aiohttp.ClientSession, keyword: str) -> dict:
    """Tries Wikipedia first. If it fails, instantly falls back to DuckDuckGo Web Search."""
    
    # 1. ATTEMPT WIKIPEDIA
    formatted_keyword = quote(keyword.strip().title().replace(" ", "_"))
    wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_keyword}"
    headers = {"User-Agent": "IRIS-Desktop-App/2.0 (Windows)", "Accept": "application/json"}
    
    try:
        async with session.get(wiki_url, headers=headers, timeout=aiohttp.ClientTimeout(total=3.0)) as resp:
            if resp.status == 200:
                data = await resp.json()
                extract = data.get("extract", "")
                if extract:
                    return {
                        "text": clean_scraped_text(extract),
                        "is_location": "coordinates" in data,
                        "source": "Wikipedia"
                    }
    except Exception:
        pass # Silently catch Wiki failures and move to fallback

    # 2. WIKIPEDIA FAILED -> FALLBACK TO DUCKDUCKGO TEXT SEARCH
    loop = asyncio.get_event_loop()
    def _scrape_ddg_text():
        try:
            results = list(DDGS().text(keyword, max_results=3))
            return clean_ddg_text(results)
        except Exception:
            return []
            
    ddg_snippets = await loop.run_in_executor(None, _scrape_ddg_text)
    
    if ddg_snippets:
        return {
            "text": ddg_snippets,
            "is_location": False,
            "source": "DuckDuckGo Web"
        }
        
    # 3. TOTAL FAILURE
    return {"text": [f"No verifiable information found for '{keyword}' across primary and fallback sources."], "is_location": False, "source": "None"}


async def fetch_media(keyword: str, count: int = 3) -> list[str]:
    loop = asyncio.get_event_loop()
    def _scrape():
        try:
            return [img["image"] for img in DDGS().images(keyword, max_results=count) if "image" in img]
        except Exception:
            return []
    return await loop.run_in_executor(None, _scrape)


async def scrape_topic(parsed_data: dict) -> dict:
    category = parsed_data["category"]
    entity = parsed_data["entity"]
    
    if category == "MATH EVALUATION":
        return {
            "entity": entity,
            "category": category,
            "show_maps": False,
            "full_text": f"Result: {parsed_data['result']}",
            "images": [],
            "map_macro": "",
            "map_micro": ""
        }
        
    async with aiohttp.ClientSession() as session:
        # Launch Text (Wiki+DDG) and Images concurrently
        text_task = fetch_text_data(session, entity)
        media_task = fetch_media(entity, count=3)
        
        text_res, images = await asyncio.gather(text_task, media_task)
        
        show_maps = (category == "location") or text_res["is_location"]
        final_category = "location" if show_maps else category
        q = quote(entity)
        
        return {
            "entity": entity.title(),
            "category": final_category,
            "show_maps": show_maps,
            "sentences": text_res["text"],
            "full_text": " ".join(text_res["text"]),
            "images": images,
            "map_macro": f"https://maps.google.com/maps?q={q}&t=m&z=4&output=embed" if show_maps else "",
            "map_micro": f"https://maps.google.com/maps?q={q}&t=k&z=14&output=embed" if show_maps else ""
        }