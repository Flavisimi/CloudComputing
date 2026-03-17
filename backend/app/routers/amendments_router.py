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
async def list_all_amendments(
    page: int = Query(1, ge=1),
    approved: Optional[str] = None,
    sort: Optional[str] = None,
    order: Optional[str] = None,
):
    params = {"page": page}
    if approved is not None: params["approved"] = approved
    if sort:  params["sort"] = sort
    if order: params["order"] = order
    data, code = await laws_service.get_all_amendments(params)
    return _resp(data, code)


@router.get("/{amendment_id}")
async def get_amendment(amendment_id: str):
    data, code = await laws_service.get_amendment(amendment_id)
    return _resp(data, code)


@router.patch("/{amendment_id}")
async def update_amendment(amendment_id: str, body: dict):
    data, code = await laws_service.update_amendment(amendment_id, body)
    return _resp(data, code)


@router.delete("/{amendment_id}")
async def delete_amendment(amendment_id: str):
    data, code = await laws_service.delete_amendment(amendment_id)
    return _resp(data, code)