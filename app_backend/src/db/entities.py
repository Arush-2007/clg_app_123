from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class UserEntity(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    firebase_uid: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    source: Mapped[str] = mapped_column(String(64), default="email-password")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ClubEntity(Base):
    __tablename__ = "clubs"
    __table_args__ = (UniqueConstraint("parent_college", "club_name", name="uq_college_club"),)

    club_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    parent_college: Mapped[str] = mapped_column(String(120), index=True)
    club_name: Mapped[str] = mapped_column(String(120), index=True)
    club_admin: Mapped[str] = mapped_column(String(120))
    club_admin_email: Mapped[str] = mapped_column(String(320))
    members: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str] = mapped_column(Text)
    c_id: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PositionEntity(Base):
    __tablename__ = "positions"
    __table_args__ = (UniqueConstraint("c_id", "hierarchy", name="uq_club_hierarchy"),)

    position_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    c_id: Mapped[str] = mapped_column(String(256), ForeignKey("clubs.c_id", ondelete="CASCADE"), index=True)
    hierarchy: Mapped[int] = mapped_column(Integer)
    hierarchy_holders: Mapped[int] = mapped_column(Integer)
    position_name: Mapped[str] = mapped_column(String(120), default="Member")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EventEntity(Base):
    __tablename__ = "events"

    event_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(120), index=True)
    image_url: Mapped[str] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(40), index=True)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProfileEntity(Base):
    __tablename__ = "profiles"

    profile_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    firebase_uid: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    college: Mapped[str] = mapped_column(String(120))
    year_of_graduation: Mapped[str] = mapped_column(String(10))
    branch: Mapped[str] = mapped_column(String(120))
    avatar_url: Mapped[str] = mapped_column(String(512))
    latitude: Mapped[str] = mapped_column(String(64), default="Not specified")
    longitude: Mapped[str] = mapped_column(String(64), default="Not specified")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
