from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.profile import PCOSProfile
from models.diet import DietPlan, Meal
from schemas.main import DietPlanOut
from services.diet_generator import generate_diet_plan
import uuid

router = APIRouter(prefix="/diet", tags=["Diet Plans"])


@router.get("/today", response_model=DietPlanOut)
async def get_today_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()
    result = await db.execute(
        select(DietPlan).where(
            DietPlan.user_id == current_user.id,
            DietPlan.plan_date == today,
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="No plan for today. Call /diet/generate to create one.")

    meal_result = await db.execute(select(Meal).where(Meal.diet_plan_id == plan.id).order_by(Meal.sort_order))
    plan.meals = meal_result.scalars().all()
    return DietPlanOut.model_validate(plan)


@router.post("/generate", response_model=DietPlanOut, status_code=201)
async def generate_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Load profile
    profile_result = await db.execute(
        select(PCOSProfile).where(PCOSProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=400, detail="Complete your profile before generating a diet plan")

    today = date.today()

    # Delete existing today's plan
    existing = await db.execute(
        select(DietPlan).where(DietPlan.user_id == current_user.id, DietPlan.plan_date == today)
    )
    old_plan = existing.scalar_one_or_none()
    if old_plan:
        await db.delete(old_plan)
        await db.flush()

    # Generate via AI
    plan_data = await generate_diet_plan(profile)

    plan = DietPlan(
        id=uuid.uuid4(),
        user_id=current_user.id,
        plan_date=today,
        total_cal=plan_data.get("total_cal"),
        total_protein_g=plan_data.get("total_protein_g"),
        total_carbs_g=plan_data.get("total_carbs_g"),
        total_fat_g=plan_data.get("total_fat_g"),
        notes=plan_data.get("notes"),
        generated_by="ai",
    )
    db.add(plan)
    await db.flush()

    meals = []
    for m in plan_data.get("meals", []):
        meal = Meal(
            id=uuid.uuid4(),
            diet_plan_id=plan.id,
            meal_type=m.get("meal_type", "snack"),
            name=m.get("name", ""),
            emoji=m.get("emoji"),
            description=m.get("description"),
            calories=m.get("calories"),
            protein_g=m.get("protein_g"),
            carbs_g=m.get("carbs_g"),
            fat_g=m.get("fat_g"),
            fiber_g=m.get("fiber_g"),
            gi_level=m.get("gi_level"),
            tags=m.get("tags", []),
            sort_order=m.get("sort_order", 0),
        )
        db.add(meal)
        meals.append(meal)

    await db.commit()
    await db.refresh(plan)
    plan.meals = meals
    return DietPlanOut.model_validate(plan)


@router.get("/history", response_model=list[DietPlanOut])
async def get_diet_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 7,
):
    result = await db.execute(
        select(DietPlan)
        .where(DietPlan.user_id == current_user.id)
        .order_by(DietPlan.plan_date.desc())
        .limit(limit)
    )
    plans = result.scalars().all()
    for plan in plans:
        meal_result = await db.execute(
            select(Meal).where(Meal.diet_plan_id == plan.id).order_by(Meal.sort_order)
        )
        plan.meals = meal_result.scalars().all()
    return [DietPlanOut.model_validate(p) for p in plans]
