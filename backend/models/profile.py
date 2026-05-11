import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Numeric, Date, SmallInteger, func, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base


class PCOSProfile(Base):
    __tablename__ = "pcos_profiles"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id             = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    age                 = Column(SmallInteger)
    weight_kg           = Column(Numeric(5, 2))
    height_cm           = Column(Numeric(5, 2))
    bmi                 = Column(Numeric(4, 2))
    diagnosis_year      = Column(SmallInteger)
    dietary_preference  = Column(String(50), default="no_restriction")
    activity_level      = Column(String(30), default="moderate")
    cycle_length_days   = Column(SmallInteger)
    last_period_date    = Column(Date)
    stress_level        = Column(SmallInteger)
    sleep_hours         = Column(Numeric(3, 1))
    symptoms            = Column(ARRAY(String), default=[])
    allergies           = Column(ARRAY(String), default=[])
    goals               = Column(ARRAY(String), default=[])
    onboarding_complete = Column(Boolean, default=False)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")
