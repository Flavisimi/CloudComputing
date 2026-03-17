import httpx
from app.config import settings

BASE = settings.laws_api_url


async def _get(path: str, params: dict = None):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{BASE}{path}", params=params)
        return r.json(), r.status_code


async def _post(path: str, body):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{BASE}{path}", json=body)
        return r.json(), r.status_code


async def _patch(path: str, body: dict):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.patch(f"{BASE}{path}", json=body)
        return r.json(), r.status_code


async def _put(path: str, body: dict):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.put(f"{BASE}{path}", json=body)
        return r.json(), r.status_code


async def _delete(path: str):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.delete(f"{BASE}{path}")
        return r.json(), r.status_code


# Laws
async def get_laws(params):         return await _get("/laws", params)
async def create_law(body):         return await _post("/laws", body)
async def get_law(id):              return await _get(f"/laws/{id}")
async def update_law(id, body):     return await _patch(f"/laws/{id}", body)
async def replace_law(id, body):    return await _put(f"/laws/{id}", body)
async def delete_law(id):           return await _delete(f"/laws/{id}")

# Tags
async def get_all_tags(params):         return await _get("/tags", params)
async def get_law_tags(id):             return await _get(f"/laws/{id}/tags")
async def add_tag(id, body):            return await _post(f"/laws/{id}/tags", body)
async def remove_tag(id, tag):          return await _delete(f"/laws/{id}/tags/{tag}")

# Articles
async def get_articles(params):                 return await _get("/articles", params)
async def get_law_articles(law_id, params):     return await _get(f"/laws/{law_id}/articles", params)
async def create_article(law_id, body):         return await _post(f"/laws/{law_id}/articles", body)
async def get_article(id):                      return await _get(f"/articles/{id}")
async def update_article(id, body):             return await _patch(f"/articles/{id}", body)
async def delete_article(id):                   return await _delete(f"/articles/{id}")
async def get_versions(id, params):             return await _get(f"/articles/{id}/versions", params)

# Amendments
async def get_all_amendments(params):               return await _get("/amendments", params)
async def get_article_amendments(id, params):       return await _get(f"/articles/{id}/amendments", params)
async def create_amendment(id, body):               return await _post(f"/articles/{id}/amendments", body)
async def get_amendment(id):                        return await _get(f"/amendments/{id}")
async def update_amendment(id, body):               return await _patch(f"/amendments/{id}", body)
async def delete_amendment(id):                     return await _delete(f"/amendments/{id}")

# References
async def get_refs_out(id):         return await _get(f"/articles/{id}/references")
async def get_refs_in(id):          return await _get(f"/articles/{id}/references/incoming")
async def add_ref(id, body):        return await _post(f"/articles/{id}/references", body)
async def delete_ref(id, to):       return await _delete(f"/articles/{id}/references/{to}")

# Stats
async def stats_per_category():     return await _get("/stats/laws-per-category")
async def stats_most_amended():     return await _get("/stats/most-amended-laws")
async def stats_article_count():    return await _get("/stats/articles-count")
async def stats_amend_per_year():   return await _get("/stats/amendments-per-year")

# Audit
async def get_audit(params):        return await _get("/audit", params)

# Bulk
async def bulk_create(body):        return await _post("/bulk/laws", body)