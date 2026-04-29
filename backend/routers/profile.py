from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.profile import PCOSProfile
from schemas.main import ProfileCreate, ProfileOut
import uuid

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/", response_model=ProfileOut)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(PCOSProfile).where(PCOSProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileOut.model_validate(profile)


@router.post("/", response_model=ProfileOut, status_code=201)
async def create_profile(
    data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(PCOSProfile).where(PCOSProfile.user_id == current_user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Profile already exists, use PUT to update")

    bmi = None
    if data.weight_kg and data.height_cm:
        bmi = round(data.weight_kg / ((data.height_cm / 100) ** 2), 2)

    profile = PCOSProfile(
        id=uuid.uuid4(),
        user_id=current_user.id,
        bmi=bmi,
        **data.model_dump(exclude_none=False),
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return ProfileOut.model_validate(profile)


@router.put("/", response_model=ProfileOut)
async def update_profile(
    data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(PCOSProfile).where(PCOSProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    update_data = data.model_dump(exclude_none=True)
    if "weight_kg" in update_data and "height_cm" in update_data:
        update_data["bmi"] = round(
            update_data["weight_kg"] / ((update_data["height_cm"] / 100) ** 2), 2
        )

    for k, v in update_data.items():
        setattr(profile, k, v)

    await db.commit()
    await db.refresh(profile)
    return ProfileOut.model_validate(profile)
