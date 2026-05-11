import uuid
from sqlalchemy import Column, String, Integer, Numeric, Date, SmallInteger, DateTime, func, ForeignKey, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base


class DietPlan(Base):
    __tablename__ = "diet_plans"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id         = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_date       = Column(Date, nullable=False)
    plan_type       = Column(String(30), default="daily")
    total_cal       = Column(Integer)
    total_protein_g = Column(Numeric(6, 1))
    total_carbs_g   = Column(Numeric(6, 1))
    total_fat_g     = Column(Numeric(6, 1))
    notes           = Column(Text)
    generated_by    = Column(String(20), default="ai")
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    user  = relationship("User", back_populates="diet_plans")
    meals = relationship("Meal", back_populates="diet_plan", cascade="all, delete-orphan", order_by="Meal.sort_order")


class Meal(Base):
    __tablename__ = "meals"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    diet_plan_id = Column(UUID(as_uuid=True), ForeignKey("diet_plans.id", ondelete="CASCADE"), nullable=False)
    meal_type    = Column(String(20), nullable=False)
    name         = Column(String(200), nullable=False)
    emoji        = Column(String(10))
    description  = Column(Text)
    calories     = Column(Integer)
    protein_g    = Column(Numeric(5, 1))
    carbs_g      = Column(Numeric(5, 1))
    fat_g        = Column(Numeric(5, 1))
    fiber_g      = Column(Numeric(5, 1))
    gi_level     = Column(String(10))
    tags         = Column(ARRAY(String), default=[])
    recipe_url   = Column(Text)
    sort_order   = Column(SmallInteger, default=0)

    diet_plan = relationship("DietPlan", back_populates="meals")
