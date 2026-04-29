import uuid
from sqlalchemy import (Column, String, Integer, Boolean, DateTime, Date,
                         SmallInteger, Text, func, ForeignKey, ARRAY)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base


# ── CHAT ──────────────────────────────────────────────
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id       = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title         = Column(String(200))
    started_at    = Column(DateTime(timezone=True), server_default=func.now())
    ended_at      = Column(DateTime(timezone=True))
    message_count = Column(Integer, default=0)

    user     = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.sent_at")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"))
    role       = Column(String(10), nullable=False)
    content    = Column(Text, nullable=False)
    tokens_used = Column(Integer)
    sent_at    = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")


# ── COMMUNITY ─────────────────────────────────────────
class CommunityGroup(Base):
    __tablename__ = "community_groups"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name         = Column(String(200), unique=True)
    description  = Column(Text)
    emoji        = Column(String(10))
    category     = Column(String(50))
    color_hex    = Column(String(7))
    member_count = Column(Integer, default=0)
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    posts   = relationship("Post", back_populates="group", cascade="all, delete-orphan")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")


class GroupMember(Base):
    __tablename__ = "group_members"

    group_id  = Column(UUID(as_uuid=True), ForeignKey("community_groups.id", ondelete="CASCADE"), primary_key=True)
    user_id   = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    role      = Column(String(20), default="member")

    group = relationship("CommunityGroup", back_populates="members")


class Post(Base):
    __tablename__ = "posts"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id      = Column(UUID(as_uuid=True), ForeignKey("community_groups.id", ondelete="CASCADE"))
    author_id     = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    content       = Column(Text, nullable=False)
    image_url     = Column(Text)
    like_count    = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    is_pinned     = Column(Boolean, default=False)
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    group    = relationship("CommunityGroup", back_populates="posts")
    author   = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id    = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"))
    author_id  = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    content    = Column(Text, nullable=False)
    like_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship("Post", back_populates="comments")


# ── EDUCATIONAL CONTENT ───────────────────────────────
class EducationalContent(Base):
    __tablename__ = "educational_content"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title         = Column(String(300), nullable=False)
    content_type  = Column(String(20), nullable=False)
    description   = Column(Text)
    emoji         = Column(String(10))
    thumbnail_url = Column(Text)
    content_url   = Column(Text)
    duration_min  = Column(SmallInteger)
    author        = Column(String(200))
    tags          = Column(ARRAY(String), default=[])
    view_count    = Column(Integer, default=0)
    like_count    = Column(Integer, default=0)
    is_featured   = Column(Boolean, default=False)
    is_active     = Column(Boolean, default=True)
    published_at  = Column(DateTime(timezone=True), server_default=func.now())


# ── CYCLE TRACKING ────────────────────────────────────
class CycleEntry(Base):
    __tablename__ = "cycle_entries"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id      = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    entry_date   = Column(Date, nullable=False)
    phase        = Column(String(30))
    cycle_day    = Column(SmallInteger)
    flow_level   = Column(String(20))
    symptoms     = Column(ARRAY(String), default=[])
    mood_score   = Column(SmallInteger)
    energy_score = Column(SmallInteger)
    pain_level   = Column(SmallInteger)
    notes        = Column(Text)
    logged_at    = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="cycle_entries")


# ── STREAK ────────────────────────────────────────────
class UserStreak(Base):
    __tablename__ = "user_streaks"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id          = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    current_streak   = Column(Integer, default=0)
    longest_streak   = Column(Integer, default=0)
    last_active_date = Column(Date)
    total_points     = Column(Integer, default=0)
    updated_at       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="streak")
