import uuid
from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email         = Column(String(255), unique=True, nullable=False, index=True)
    username      = Column(String(100), unique=True, nullable=False)
    full_name     = Column(String(200), nullable=False)
    password_hash = Column(String, nullable=False)
    avatar_url    = Column(String, nullable=True)
    is_active     = Column(Boolean, default=True)
    is_verified   = Column(Boolean, default=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # relationships
    profile       = relationship("PCOSProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    diet_plans    = relationship("DietPlan", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    posts         = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    cycle_entries = relationship("CycleEntry", back_populates="user", cascade="all, delete-orphan")
    streak        = relationship("UserStreak", back_populates="user", uselist=False, cascade="all, delete-orphan")
    user_content  = relationship("UserContent", back_populates="user", cascade="all, delete-orphan")
