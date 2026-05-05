

from sqlmodel import Session, create_engine, select
import backend.app.utils.settings as settings
from backend.app.models.role import Role
from backend.app.models.user import UserCreate
from backend.app.services.user_services import register_user
from backend.app.crud import user_crud
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

def insert_root_user():
    for session in get_session():
        server_settings = settings.get_server_settings()
        email = server_settings.root_user_email
        password = server_settings.root_user_password
        
        # Check if the root user exists
        existing_user = user_crud.get_user_by_email(session, email=email)
        if not existing_user:
            admin_role = session.exec(select(Role).where(Role.name == "admin")).first()
            if admin_role:
                from backend.app.error import EmailAlreadyRegisteredError, InvalidUserDataError
                try:
                    user_create = UserCreate(
                        name="Root Admin",
                        email=email,
                        password=password,
                        role_id=admin_role.id
                    )
                    register_user(session, user_create)
                except (EmailAlreadyRegisteredError, InvalidUserDataError):
                    pass
        session.commit()