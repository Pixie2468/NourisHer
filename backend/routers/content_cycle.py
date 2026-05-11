from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.other import EducationalContent, CycleEntry
from schemas.main import ContentOut, CycleEntryCreate, CycleEntryOut
import uuid
from datetime import date

# ── CONTENT ROUTER ───────────────────────────────────────────
content_router = APIRouter(prefix="/content", tags=["Educational Content"])


@content_router.get("/", response_model=list[ContentOut])
async def list_content(
    content_type: str = None,
    featured: bool = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(EducationalContent).where(EducationalContent.is_active == True)
    if content_type:
        query = query.where(EducationalContent.content_type == content_type)
    if featured is not None:
        query = query.where(EducationalContent.is_featured == featured)
    query = query.order_by(EducationalContent.is_featured.desc(), EducationalContent.published_at.desc())

    result = await db.execute(query)
    return [ContentOut.model_validate(c) for c in result.scalars().all()]


@content_router.get("/{content_id}", response_model=ContentOut)
async def get_content(
    content_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await db.get(EducationalContent, content_id)
    if not content or not content.is_active:
        raise HTTPException(status_code=404, detail="Content not found")
    content.view_count = (content.view_count or 0) + 1
    await db.commit()
    return ContentOut.model_validate(content)


@content_router.post("/{content_id}/like")
async def like_content(
    content_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await db.get(EducationalContent, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    content.like_count = (content.like_count or 0) + 1
    await db.commit()
    return {"like_count": content.like_count}


# ── CYCLE ROUTER ─────────────────────────────────────────────
cycle_router = APIRouter(prefix="/cycle", tags=["Cycle Tracking"])


@cycle_router.get("/", response_model=list[CycleEntryOut])
async def list_entries(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 90,
):
    result = await db.execute(
        select(CycleEntry)
        .where(CycleEntry.user_id == current_user.id)
        .order_by(CycleEntry.entry_date.desc())
        .limit(limit)
    )
    return [CycleEntryOut.model_validate(e) for e in result.scalars().all()]


@cycle_router.post("/", response_model=CycleEntryOut, status_code=201)
async def log_entry(
    data: CycleEntryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(CycleEntry).where(CycleEntry.user_id == current_user.id, CycleEntry.entry_date == data.entry_date)
    )
    entry = existing.scalar_one_or_none()

    if entry:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(entry, k, v)
    else:
        entry = CycleEntry(id=uuid.uuid4(), user_id=current_user.id, **data.model_dump())
        db.add(entry)

    await db.commit()
    await db.refresh(entry)
    return CycleEntryOut.model_validate(entry)


@cycle_router.get("/today", response_model=CycleEntryOut)
async def get_today_entry(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CycleEntry).where(CycleEntry.user_id == current_user.id, CycleEntry.entry_date == date.today())
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="No entry for today")
    return CycleEntryOut.model_validate(entry)
