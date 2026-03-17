import httpx
from app.config import settings

# Cheia vine din settings care o citește din .env / variabile de environment
# Nu există niciun secret hardcodat în acest fișier


async def search(query: str, page_size: int = 5) -> dict:
    if not settings.news_api_key:
        return {
            "error": "NEWS_API_KEY not configured. Add it to your .env file (get a free key at newsapi.org)",
            "articles": [],
        }

    params = {
        "q": query,
        "apiKey": settings.news_api_key,   # citit din env, nu hardcodat
        "language": "en",
        "pageSize": page_size,
        "sortBy": "relevancy",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(settings.news_api_url, params=params)

            if r.status_code == 401:
                return {"error": "Invalid NEWS_API_KEY. Check your .env file.", "articles": []}
            if r.status_code == 429:
                return {"error": "NewsAPI rate limit exceeded (100 req/day on free plan)", "articles": []}

            r.raise_for_status()
            data = r.json()

            return {
                "totalResults": data.get("totalResults", 0),
                "articles": [
                    {
                        "title": a.get("title"),
                        "description": a.get("description"),
                        "url": a.get("url"),
                        "publishedAt": a.get("publishedAt"),
                        "source": a.get("source", {}).get("name"),
                        "urlToImage": a.get("urlToImage"),
                    }
                    for a in data.get("articles", [])
                    if a.get("title") != "[Removed]"
                ],
            }
    except httpx.TimeoutException:
        return {"error": "NewsAPI timeout", "articles": []}
    except Exception as e:
        return {"error": str(e), "articles": []}