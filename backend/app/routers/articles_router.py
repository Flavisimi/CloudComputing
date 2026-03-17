from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from app.services import laws_service

router = APIRouter()


def _resp(data, status: int):
    if status >= 500:
        raise HTTPException(status_code=502, detail=data)
    return JSONResponse(content=data, status_code=status)


@router.get("")
async def list_articles(
    page: int = Query(1, ge=1),
    law_id: Optional[str] = None,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    order: Optional[str] = None,
):
    params = {"page": page}
    if law_id:  params["law_id"] = law_id
    if search:  params["search"] = search
    if sort:    params["sort"] = sort
    if order:   params["order"] = order
    data, code = await laws_service.get_articles(params)
    return _resp(data, code)


@router.get("/{article_id}")
async def get_article(article_id: str):
    data, code = await laws_service.get_article(article_id)
    return _resp(data, code)


@router.patch("/{article_id}")
async def update_article(article_id: str, body: dict):
    data, code = await laws_service.update_article(article_id, body)
    return _resp(data, code)


@router.delete("/{article_id}")
async def delete_article(article_id: str):
    data, code = await laws_service.delete_article(article_id)
    return _resp(data, code)


@router.get("/{article_id}/versions")
async def get_versions(article_id: str, page: int = Query(1, ge=1)):
    data, code = await laws_service.get_versions(article_id, {"page": page})
    return _resp(data, code)


@router.get("/{article_id}/amendments")
async def get_amendments(
    article_id: str,
    page: int = Query(1, ge=1),
    approved: Optional[str] = None,
):
    params = {"page": page}
    if approved is not None:
        params["approved"] = approved
    data, code = await laws_service.get_article_amendments(article_id, params)
    return _resp(data, code)


@router.post("/{article_id}/amendments", status_code=201)
async def create_amendment(article_id: str, body: dict):
    data, code = await laws_service.create_amendment(article_id, body)
    return _resp(data, code)


@router.get("/{article_id}/references")
async def get_refs_out(article_id: str):
    data, code = await laws_service.get_refs_out(article_id)
    return _resp(data, code)


@router.get("/{article_id}/references/incoming")
async def get_refs_in(article_id: str):
    data, code = await laws_service.get_refs_in(article_id)
    return _resp(data, code)


@router.post("/{article_id}/references", status_code=201)
async def add_ref(article_id: str, body: dict):
    data, code = await laws_service.add_ref(article_id, body)
    return _resp(data, code)


@router.delete("/{article_id}/references/{to_id}")
async def delete_ref(article_id: str, to_id: str):
    data, code = await laws_service.delete_ref(article_id, to_id)
    return _resp(data, code)