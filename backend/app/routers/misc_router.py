from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from app.services import laws_service, wikipedia_service, news_service

router = APIRouter()


def _resp(data, status: int):
    if status >= 500:
        raise HTTPException(502, detail=data)
    return JSONResponse(content=data, status_code=status)


@router.get("/tags")
async def get_all_tags(search: Optional[str] = None):
    params = {}
    if search:
        params["search"] = search
    data, code = await laws_service.get_all_tags(params)
    return _resp(data, code)


@router.get("/audit")
async def get_audit(
    page: int = Query(1, ge=1),
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
):
    params = {"page": page}
    if entity_type: params["entity_type"] = entity_type
    if action:      params["action"] = action
    data, code = await laws_service.get_audit(params)
    return _resp(data, code)


@router.post("/bulk/laws", status_code=201)
async def bulk_create(body: list):
    data, code = await laws_service.bulk_create(body)
    return _resp(data, code)


@router.get("/wikipedia/search")
async def wikipedia_search(q: str, limit: int = Query(3, ge=1, le=10)):
    results = await wikipedia_service.search(q, limit)
    return {"query": q, "results": results}


@router.get("/wikipedia/summary")
async def wikipedia_summary(title: str):
    return await wikipedia_service.get_summary(title)


@router.get("/news/search")
async def news_search(q: str, page_size: int = Query(5, ge=1, le=20)):
    return await news_service.search(q, page_size)