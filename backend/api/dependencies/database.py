

from sqlmodel import Session, create_engine, select
import backend.app.settings as settings
from backend.app.models.role import Role
from collections.abc import Iterator

# Create the engine once globally to avoid recreating the connection pool on every request
engine = create_engine(settings.get_server_settings().database_url)

def get_session() -> Iterator[Session]:
    """Dependency that provides a SQLAlchemy session."""
    with Session(engine) as session:
        yield session


def insert_default_roles():
    # Initialize default roles
    default_roles = ["admin", "user"]
    for session in get_session():
        for role_name in default_roles:
            existing_role = session.exec(select(Role).where(Role.name == role_name)).first()
            if not existing_role:
                session.add(Role(name=role_name))
        session.commit()