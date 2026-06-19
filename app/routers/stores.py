"""Store listing and manual scrape trigger."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.schemas import StoreOut
from app.scrapers.registry import STORE_DEFS
from app.services import products as svc

router = APIRouter(prefix="/api", tags=["stores"])


@router.get("/stores", response_model=list[StoreOut])
async def list_stores(db: AsyncSession = Depends(get_db)):
    return await svc.list_stores(db)


@router.post("/admin/scrape/{store}")
async def trigger_scrape(store: str):
    from app.services.scheduler import scrape_all, scrape_store

    if store == "all":
        return {"results": await scrape_all()}
    if store not in STORE_DEFS:
        raise HTTPException(status_code=404, detail="Unknown store")
    return await scrape_store(store)
