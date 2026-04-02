from datetime import datetime, timezone

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
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


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
    status: Mapped[str] = mapped_column(
        String(20), default="pending", index=True
    )
    # pending | verified | rejected
    document_url: Mapped[str | None] = mapped_column(
        String(512), nullable=True
    )
    account_manager_uid: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    college_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("colleges.id", ondelete="SET NULL"),
        nullable=True, index=True
    )
    rejection_reason: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ClubMemberEntity(Base):
    __tablename__ = "club_members"
    __table_args__ = (
        UniqueConstraint("club_id", "firebase_uid", name="uq_club_member"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    club_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clubs.club_id", ondelete="CASCADE"), index=True
    )
    firebase_uid: Mapped[str] = mapped_column(String(128), index=True)
    position_name: Mapped[str] = mapped_column(String(120), default="Member")
    hierarchy: Mapped[int] = mapped_column(Integer, default=99)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class ClubAccountEntity(Base):
    __tablename__ = "club_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    club_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clubs.club_id", ondelete="CASCADE"),
        unique=True, index=True
    )
    # firebase_uid of the student who can switch to club profile
    managed_by_uid: Mapped[str] = mapped_column(String(128), index=True)
    club_avatar_url: Mapped[str | None] = mapped_column(
        String(512), nullable=True
    )
    club_bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class PositionEntity(Base):
    __tablename__ = "positions"
    __table_args__ = (UniqueConstraint("c_id", "hierarchy", name="uq_club_hierarchy"),)

    position_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    c_id: Mapped[str] = mapped_column(String(256), ForeignKey("clubs.c_id", ondelete="CASCADE"), index=True)
    hierarchy: Mapped[int] = mapped_column(Integer)
    hierarchy_holders: Mapped[int] = mapped_column(Integer)
    position_name: Mapped[str] = mapped_column(String(120), default="Member")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class EventEntity(Base):
    __tablename__ = "events"

    event_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(120), index=True)
    image_url: Mapped[str] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(40), index=True)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    creator_uid: Mapped[str | None] = mapped_column(
        String(128), nullable=True, index=True
    )
    event_type: Mapped[str] = mapped_column(
        String(20), default="offline"
    )
    registration_url: Mapped[str | None] = mapped_column(
        String(512), nullable=True
    )
    max_registrations: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    college_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("colleges.id", ondelete="SET NULL"),
        nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


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
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    # stored as comma-separated string e.g. "Python,Flutter,FastAPI"

    social_links: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    # stored as JSON string e.g. '{"linkedin":"url","github":"url"}'

    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    is_alumni: Mapped[bool] = mapped_column(Boolean, default=False)
    college_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("colleges.id", ondelete="SET NULL"),
        nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class AdminEntity(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    firebase_uid: Mapped[str] = mapped_column(
        String(128), unique=True, index=True
    )
    added_by_uid: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class CollegeEntity(Base):
    __tablename__ = "colleges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    college_code: Mapped[str] = mapped_column(
        String(50), unique=True, index=True
    )
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class CollegeAdminEntity(Base):
    __tablename__ = "college_admins"
    __table_args__ = (
        UniqueConstraint("college_id", "firebase_uid",
                         name="uq_college_admin"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    college_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True
    )
    firebase_uid: Mapped[str] = mapped_column(String(128), index=True)
    added_by_uid: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class FollowEntity(Base):
    __tablename__ = "follows"
    __table_args__ = (
        UniqueConstraint("follower_uid", "followee_id", "followee_type",
                         name="uq_follow"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    follower_uid: Mapped[str] = mapped_column(String(128), index=True)
    followee_id: Mapped[int] = mapped_column(Integer, index=True)
    # "club" | "body" — extensible for future entity types
    followee_type: Mapped[str] = mapped_column(String(50), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class ConnectionEntity(Base):
    __tablename__ = "connections"
    __table_args__ = (
        UniqueConstraint("requester_uid", "receiver_uid",
                         name="uq_connection"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    requester_uid: Mapped[str] = mapped_column(String(128), index=True)
    receiver_uid: Mapped[str] = mapped_column(String(128), index=True)
    # pending | accepted | rejected | blocked
    status: Mapped[str] = mapped_column(
        String(20), default="pending", index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )


class TagEntity(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    tag_type: Mapped[str] = mapped_column(String(50), index=True)
    # e.g. "club_president","branch_topper","student_of_year","fresher_king"
    college_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("colleges.id", ondelete="SET NULL"),
        nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class UserTagEntity(Base):
    __tablename__ = "user_tags"
    __table_args__ = (
        UniqueConstraint("firebase_uid", "tag_id", name="uq_user_tag"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    firebase_uid: Mapped[str] = mapped_column(String(128), index=True)
    tag_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tags.id", ondelete="CASCADE"), index=True
    )
    granted_by_uid: Mapped[str] = mapped_column(String(128))
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class FeedItemEntity(Base):
    __tablename__ = "feed_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    creator_uid: Mapped[str] = mapped_column(String(128), index=True)
    # "user" | "club" | "admin"
    creator_type: Mapped[str] = mapped_column(String(20), index=True)
    # "post" | "reel" | "event" | "notice"
    content_type: Mapped[str] = mapped_column(String(20), index=True)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_url: Mapped[str | None] = mapped_column(
        String(512), nullable=True
    )
    # "image" | "video" | None
    media_type: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )
    college_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("colleges.id", ondelete="SET NULL"),
        nullable=True, index=True
    )
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )


class FeedLikeEntity(Base):
    __tablename__ = "feed_likes"
    __table_args__ = (
        UniqueConstraint("feed_item_id", "firebase_uid",
                         name="uq_feed_like"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    feed_item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("feed_items.id", ondelete="CASCADE"),
        index=True
    )
    firebase_uid: Mapped[str] = mapped_column(String(128), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class FeedReportEntity(Base):
    __tablename__ = "feed_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    feed_item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("feed_items.id", ondelete="CASCADE"),
        index=True
    )
    reported_by_uid: Mapped[str] = mapped_column(String(128), index=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class EventRegistrationEntity(Base):
    __tablename__ = "event_registrations"
    __table_args__ = (
        UniqueConstraint("event_id", "firebase_uid",
                         name="uq_event_registration"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("events.event_id", ondelete="CASCADE"),
        index=True
    )
    firebase_uid: Mapped[str] = mapped_column(String(128), index=True)
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class ProfileCertificateEntity(Base):
    __tablename__ = "profile_certificates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    firebase_uid: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str] = mapped_column(String(200))
    issued_by: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )
    file_url: Mapped[str] = mapped_column(String(512))
    issued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class WorkExperienceEntity(Base):
    __tablename__ = "work_experiences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    firebase_uid: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str] = mapped_column(String(200))
    company: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # if end_date is null and is_current is true → ongoing
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class ConversationEntity(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # "direct" | "group" | "official"
    type: Mapped[str] = mapped_column(String(20), index=True)
    # display name for group/official chats, null for direct
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(
        String(512), nullable=True
    )
    college_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("colleges.id", ondelete="SET NULL"),
        nullable=True, index=True
    )
    # for official chats — tied to a club
    club_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("clubs.club_id", ondelete="SET NULL"),
        nullable=True, index=True
    )
    created_by_uid: Mapped[str] = mapped_column(String(128), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class ConversationMemberEntity(Base):
    __tablename__ = "conversation_members"
    __table_args__ = (
        UniqueConstraint("conversation_id", "firebase_uid",
                         name="uq_conversation_member"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True
    )
    firebase_uid: Mapped[str] = mapped_column(String(128), index=True)
    # "admin" | "member"
    role: Mapped[str] = mapped_column(String(20), default="member")
    # messages after last_read_at are unread
    last_read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class MessageEntity(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True
    )
    sender_uid: Mapped[str] = mapped_column(String(128), index=True)
    content: Mapped[str] = mapped_column(Text)
    # "text" | "image" | "reel_share"
    message_type: Mapped[str] = mapped_column(
        String(20), default="text"
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
