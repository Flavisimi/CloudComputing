import asyncio
from fastapi import APIRouter
from app.services import laws_service, wikipedia_service, news_service

router = APIRouter()


@router.get("/laws/{law_id}")
async def get_enriched_law(law_id: str):
    law_data, law_status = await laws_service.get_law(law_id)

    if law_status == 404:
        return {"error": "Law not found", "law": None, "wikipedia": [], "news": {}}
    if law_status >= 400:
        return {"error": law_data, "law": None, "wikipedia": [], "news": {}}

    search_query = law_data.get("title", "")

    wiki_results, news_results = await asyncio.gather(
        wikipedia_service.search(search_query, limit=3),
        news_service.search(search_query, page_size=5),
    )

    return {
        "law": law_data,
        "wikipedia": wiki_results,
        "news": news_results,
    }


@router.get("/stats")
async def get_aggregated_stats():
    per_cat, most_amended, art_count, amend_year = await asyncio.gather(
        laws_service.stats_per_category(),
        laws_service.stats_most_amended(),
        laws_service.stats_article_count(),
        laws_service.stats_amend_per_year(),
    )
    return {
        "laws_per_category":   per_cat[0],
        "most_amended_laws":   most_amended[0],
        "articles_count":      art_count[0],
        "amendments_per_year": amend_year[0],
    }