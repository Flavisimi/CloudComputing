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
async def list_laws(
    page: int = Query(1, ge=1),
    sort: Optional[str] = None,
    order: Optional[str] = None,
    status: Optional[str] = None,
    title: Optional[str] = None,
):
    params = {"page": page}
    if sort:   params["sort"] = sort
    if order:  params["order"] = order
    if status: params["status"] = status
    if title:  params["title"] = title
    data, code = await laws_service.get_laws(params)
    return _resp(data, code)


@router.post("", status_code=201)
async def create_law(body: dict):
    data, code = await laws_service.create_law(body)
    return _resp(data, code)


@router.get("/{law_id}")
async def get_law(law_id: str):
    data, code = await laws_service.get_law(law_id)
    return _resp(data, code)


@router.patch("/{law_id}")
async def update_law(law_id: str, body: dict):
    data, code = await laws_service.update_law(law_id, body)
    return _resp(data, code)


@router.put("/{law_id}")
async def replace_law(law_id: str, body: dict):
    data, code = await laws_service.replace_law(law_id, body)
    return _resp(data, code)


@router.delete("/{law_id}")
async def delete_law(law_id: str):
    data, code = await laws_service.delete_law(law_id)
    return _resp(data, code)


@router.get("/{law_id}/tags")
async def get_law_tags(law_id: str):
    data, code = await laws_service.get_law_tags(law_id)
    return _resp(data, code)


@router.post("/{law_id}/tags")
async def add_tag(law_id: str, body: dict):
    data, code = await laws_service.add_tag(law_id, body)
    return _resp(data, code)


@router.delete("/{law_id}/tags/{tag_name}")
async def remove_tag(law_id: str, tag_name: str):
    data, code = await laws_service.remove_tag(law_id, tag_name)
    return _resp(data, code)


@router.get("/{law_id}/articles")
async def get_law_articles(
    law_id: str,
    page: int = Query(1, ge=1),
    sort: Optional[str] = None,
    order: Optional[str] = None,
):
    params = {"page": page}
    if sort:  params["sort"] = sort
    if order: params["order"] = order
    data, code = await laws_service.get_law_articles(law_id, params)
    return _resp(data, code)


@router.post("/{law_id}/articles", status_code=201)
async def create_article(law_id: str, body: dict):
    data, code = await laws_service.create_article(law_id, body)
    return _resp(data, code)