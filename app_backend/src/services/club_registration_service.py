from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.db.entities import ClubAccountEntity, ClubEntity, ClubMemberEntity
from src.models.clubs import ClubRegistrationRequest


def submit_club_registration(
    db: Session,
    request: ClubRegistrationRequest,
    submitted_by_uid: str,
) -> ClubEntity:
    """
    Creates a club with status=pending.
    Also creates ClubMemberEntity rows for each member.
    ClubAccountEntity is created only after admin approves.
    """
    c_id = f"{request.club_name.lower().replace(' ', '_')}_{request.parent_college.lower().replace(' ', '_')}"

    existing = db.query(ClubEntity).filter(ClubEntity.c_id == c_id).first()
    if existing:
        raise ValueError(f"Club '{request.club_name}' already exists at {request.parent_college}")

    club = ClubEntity(
        parent_college=request.parent_college,
        club_name=request.club_name,
        club_admin=submitted_by_uid,
        club_admin_email=None,
        members=len(request.members),
        description=request.description,
        c_id=c_id,
        status="pending",
        document_url=request.document_url,
        account_manager_uid=request.account_manager_uid,
    )
    db.add(club)
    db.flush()  # get club_id before adding members

    for member in request.members:
        club_member = ClubMemberEntity(
            club_id=club.club_id,
            firebase_uid=member.firebase_uid,
            position_name=member.position_name,
            hierarchy=member.hierarchy,
        )
        db.add(club_member)

    db.commit()
    db.refresh(club)
    return club


def approve_club(
    db: Session,
    club_id: int,
    account_manager_uid: str,
) -> ClubEntity:
    club = db.query(ClubEntity).filter(ClubEntity.club_id == club_id).first()
    if not club:
        raise ValueError(f"Club {club_id} not found")

    club.status = "verified"
    club.verified_at = datetime.now(timezone.utc)

    # Create the club account for the designated manager
    existing_account = db.query(ClubAccountEntity).filter(
        ClubAccountEntity.club_id == club_id
    ).first()
    if not existing_account:
        account = ClubAccountEntity(
            club_id=club_id,
            managed_by_uid=club.account_manager_uid or account_manager_uid,
            is_verified=True,
        )
        db.add(account)

    db.commit()
    db.refresh(club)
    return club


def reject_club(
    db: Session,
    club_id: int,
    reason: str | None,
) -> ClubEntity:
    club = db.query(ClubEntity).filter(ClubEntity.club_id == club_id).first()
    if not club:
        raise ValueError(f"Club {club_id} not found")

    club.status = "rejected"
    club.rejection_reason = reason
    db.commit()
    db.refresh(club)
    return club


def get_pending_clubs(db: Session) -> list[ClubEntity]:
    return db.query(ClubEntity).filter(
        ClubEntity.status == "pending"
    ).order_by(ClubEntity.created_at.desc()).all()


def get_club_members(db: Session, club_id: int) -> list[ClubMemberEntity]:
    return db.query(ClubMemberEntity).filter(
        ClubMemberEntity.club_id == club_id
    ).all()
