import httpx
import re

WIKI_SEARCH = "https://en.wikipedia.org/w/api.php"
WIKI_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary"

# Wikipedia cere User-Agent explicit — fără el blochează requesturile
HEADERS = {
    "User-Agent": "LexManager/1.0 (educational project; contact@example.com)",
    "Accept": "application/json",
}


def _clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "")


async def search(query: str, limit: int = 3) -> list:
    # Încearcă mai întâi summary direct (mai fiabil pentru titluri exacte)
    summary = await get_summary(query)
    if "error" not in summary:
        return [{
            "title": summary["title"],
            "snippet": summary["extract"][:300] + "..." if len(summary.get("extract", "")) > 300 else summary.get("extract", ""),
            "url": summary["url"],
            "thumbnail": summary.get("thumbnail"),
        }]

    # Fallback: search API
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
        "format": "json",
        "srprop": "snippet",
    }
    try:
        async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
            r = await client.get(WIKI_SEARCH, params=params)
            r.raise_for_status()
            results = r.json().get("query", {}).get("search", [])

            if not results:
                # Încearcă cu primele 2 cuvinte din titlu
                short_query = " ".join(query.split()[:2])
                r2 = await client.get(WIKI_SEARCH, params={**params, "srsearch": short_query})
                results = r2.json().get("query", {}).get("search", [])

            return [
                {
                    "title": item["title"],
                    "snippet": _clean_html(item.get("snippet", "")),
                    "url": f"https://en.wikipedia.org/wiki/{item['title'].replace(' ', '_')}",
                    "thumbnail": None,
                }
                for item in results
            ]
    except httpx.TimeoutException:
        return [{"error": "Wikipedia timeout", "title": "", "snippet": "", "url": ""}]
    except Exception as e:
        return [{"error": str(e), "title": "", "snippet": "", "url": ""}]


async def get_summary(title: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
            r = await client.get(
                f"{WIKI_SUMMARY}/{title.replace(' ', '_')}",
            )
            if r.status_code == 404:
                return {"error": "Not found"}
            r.raise_for_status()
            data = r.json()
            return {
                "title": data.get("title"),
                "extract": data.get("extract", ""),
                "thumbnail": data.get("thumbnail", {}).get("source"),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
            }
    except Exception as e:
        return {"error": str(e)}