from sqlmodel import Session, select
from backend.app.models.archive import Archive, ArchiveCreate
from backend.app.models.user import User
from backend.app.models.user_archive_link import UserArchiveLink, ArchiveRole

def create_archive(session: Session, archive: ArchiveCreate, user_id: int) -> Archive:
    db_archive = Archive.model_validate(archive)
    session.add(db_archive)
    session.commit()
    session.refresh(db_archive)

    # Automatically set the creator as the OWNER
    link = UserArchiveLink(user_id=user_id, archive_id=db_archive.id, role=ArchiveRole.OWNER)
    session.add(link)
    session.commit()
    session.refresh(db_archive)

    return db_archive

def get_archive(session: Session, archive_id: int) -> Archive | None:
    return session.get(Archive, archive_id)

def get_all_archives(session: Session, offset: int = 0, limit: int = 100) -> list[Archive]:
    return list(session.exec(select(Archive).offset(offset).limit(limit)).all())

def update_archive(session: Session, archive_id: int, archive_data: ArchiveCreate) -> Archive | None:
    db_archive = session.get(Archive, archive_id)
    if not db_archive:
        return None
    
    update_data = archive_data.model_dump(exclude_unset=True)
    db_archive.sqlmodel_update(update_data)
    session.add(db_archive)
    session.commit()
    session.refresh(db_archive)
    return db_archive

def delete_archive(session: Session, archive_id: int) -> bool:
    db_archive = session.get(Archive, archive_id)
    if not db_archive:
        return False
    session.delete(db_archive)
    session.commit()
    return True

def add_user_to_archive(session: Session, archive_id: int, user_id: int, role: ArchiveRole) -> UserArchiveLink | None:
    # Ensure they both exist
    if not session.get(Archive, archive_id) or not session.get(User, user_id):
        return None
    
    link = UserArchiveLink(user_id=user_id, archive_id=archive_id, role=role)
    session.add(link)
    session.commit()
    session.refresh(link)
    return link

def remove_user_from_archive(session: Session, archive_id: int, user_id: int) -> bool:
    statement = select(UserArchiveLink).where(
        UserArchiveLink.archive_id == archive_id,
        UserArchiveLink.user_id == user_id
    )
    link = session.exec(statement).first()
    if not link:
        return False
    session.delete(link)
    session.commit()
    return True

def get_user_archive_role(session: Session, archive_id: int, user_id: int) -> ArchiveRole | None:
    statement = select(UserArchiveLink).where(
        UserArchiveLink.archive_id == archive_id,
        UserArchiveLink.user_id == user_id
    )
    link = session.exec(statement).first()
    return link.role if link else None