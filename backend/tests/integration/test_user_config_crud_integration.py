import pytest
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, Session, create_engine

from backend.app.crud.user_config_crud import (
    create_user_config,
    delete_user_config,
    get_user_config,
    get_user_config_by_user_id,
    update_user_config,
)
from backend.app.models.user import User
from backend.app.models.user_config import UserConfig
from backend.app.models import archive as _archive_model  # noqa: F401
from backend.app.models import author as _author_model  # noqa: F401
from backend.app.models import piece as _piece_model  # noqa: F401
from backend.app.models import type as _type_model  # noqa: F401
from backend.app.models import user_archive_link as _user_archive_link_model  # noqa: F401
from backend.app.models.role import Role # noqa: F401


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    # Enforce FK constraints so tests validate relational integrity.
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        del connection_record
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def _create_user(session: Session, email: str = "user@example.com") -> User:
    user = User(name="Test User", email=email, password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_create_and_get_user_config(session: Session):
    user = _create_user(session, email="create-get@example.com")

    created = create_user_config(
        session,
        UserConfig(
            language="en",
            presets_instruments_path="data/presets/instruments",
            presets_pieces_path="data/presets/pieces",
            dossier_cover_path="data/covers/default.pdf",
            user_id=user.id,
        ),
    )

    assert created.id is not None
    fetched_by_id = get_user_config(session, created.id)
    assert fetched_by_id is not None
    assert fetched_by_id.user_id == user.id
    assert fetched_by_id.language == "en"

    fetched_by_user_id = get_user_config_by_user_id(session, user.id)
    assert fetched_by_user_id is not None
    assert fetched_by_user_id.id == created.id


def test_update_user_config_persists_changes(session: Session):
    user = _create_user(session, email="update@example.com")
    created = create_user_config(
        session,
        UserConfig(
            language="es",
            presets_instruments_path="old_inst",
            presets_pieces_path="old_pieces",
            dossier_cover_path="old_cover",
            user_id=user.id,
        ),
    )

    created.language = "en"
    created.presets_instruments_path = "new_inst"
    created.presets_pieces_path = "new_pieces"
    created.dossier_cover_path = "new_cover"

    updated = update_user_config(session, created)

    assert updated is not None
    assert updated.language == "en"
    assert updated.presets_instruments_path == "new_inst"
    assert updated.presets_pieces_path == "new_pieces"
    assert updated.dossier_cover_path == "new_cover"

    persisted = get_user_config(session, created.id)
    assert persisted is not None
    assert persisted.language == "en"


def test_delete_user_config_removes_row(session: Session):
    user = _create_user(session, email="delete@example.com")
    created = create_user_config(
        session,
        UserConfig(
            language="en",
            presets_instruments_path="inst",
            presets_pieces_path="pieces",
            dossier_cover_path="cover",
            user_id=user.id,
        ),
    )

    deleted = delete_user_config(session, created.id)

    assert deleted is True
    assert get_user_config(session, created.id) is None
    assert get_user_config_by_user_id(session, user.id) is None


def test_create_user_config_requires_existing_user(session: Session):
    with pytest.raises(IntegrityError):
        create_user_config(
            session,
            UserConfig(
                language="en",
                presets_instruments_path="inst",
                presets_pieces_path="pieces",
                dossier_cover_path="cover",
                user_id=999999,
            ),
        )
