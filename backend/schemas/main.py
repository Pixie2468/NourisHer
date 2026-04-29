from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
import uuid


# ── PROFILE ───────────────────────────────────────────
class ProfileCreate(BaseModel):
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    diagnosis_year: Optional[int] = None
    dietary_preference: Optional[str] = "no_restriction"
    activity_level: Optional[str] = "moderate"
    cycle_length_days: Optional[int] = None
    last_period_date: Optional[date] = None
    stress_level: Optional[int] = None
    sleep_hours: Optional[float] = None
    symptoms: List[str] = []
    allergies: List[str] = []
    goals: List[str] = []
    onboarding_complete: bool = False


class ProfileOut(ProfileCreate):
    id: uuid.UUID
    user_id: uuid.UUID
    bmi: Optional[float] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ── DIET ──────────────────────────────────────────────
class MealOut(BaseModel):
    id: uuid.UUID
    meal_type: str
    name: str
    emoji: Optional[str]
    description: Optional[str]
    calories: Optional[int]
    protein_g: Optional[float]
    carbs_g: Optional[float]
    fat_g: Optional[float]
    fiber_g: Optional[float]
    gi_level: Optional[str]
    tags: List[str] = []
    recipe_url: Optional[str]
    model_config = {"from_attributes": True}


class DietPlanOut(BaseModel):
    id: uuid.UUID
    plan_date: date
    plan_type: str
    total_cal: Optional[int]
    total_protein_g: Optional[float]
    total_carbs_g: Optional[float]
    total_fat_g: Optional[float]
    notes: Optional[str]
    meals: List[MealOut] = []
    model_config = {"from_attributes": True}


# ── CHAT ──────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[uuid.UUID] = None


class ChatMessageOut(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    sent_at: datetime
    model_config = {"from_attributes": True}


class ChatSessionOut(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    started_at: datetime
    message_count: int
    messages: List[ChatMessageOut] = []
    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    session_id: uuid.UUID
    reply: str
    sent_at: datetime


# ── COMMUNITY ─────────────────────────────────────────
class PostCreate(BaseModel):
    group_id: uuid.UUID
    content: str
    image_url: Optional[str] = None


class CommentCreate(BaseModel):
    content: str


class CommentOut(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID
    content: str
    like_count: int
    created_at: datetime
    model_config = {"from_attributes": True}


class PostOut(BaseModel):
    id: uuid.UUID
    group_id: uuid.UUID
    author_id: uuid.UUID
    content: str
    image_url: Optional[str]
    like_count: int
    comment_count: int
    is_pinned: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class GroupOut(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    emoji: Optional[str]
    category: Optional[str]
    color_hex: Optional[str]
    member_count: int
    model_config = {"from_attributes": True}


# ── CONTENT ───────────────────────────────────────────
class ContentOut(BaseModel):
    id: uuid.UUID
    title: str
    content_type: str
    description: Optional[str]
    emoji: Optional[str]
    thumbnail_url: Optional[str]
    content_url: Optional[str]
    duration_min: Optional[int]
    author: Optional[str]
    tags: List[str] = []
    view_count: int
    like_count: int
    is_featured: bool
    model_config = {"from_attributes": True}


# ── CYCLE ─────────────────────────────────────────────
class CycleEntryCreate(BaseModel):
    entry_date: date
    phase: Optional[str] = None
    cycle_day: Optional[int] = None
    flow_level: Optional[str] = None
    symptoms: List[str] = []
    mood_score: Optional[int] = None
    energy_score: Optional[int] = None
    pain_level: Optional[int] = None
    notes: Optional[str] = None


class CycleEntryOut(CycleEntryCreate):
    id: uuid.UUID
    user_id: uuid.UUID
    logged_at: datetime
    model_config = {"from_attributes": True}
