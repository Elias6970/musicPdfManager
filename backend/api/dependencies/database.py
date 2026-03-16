

from sqlmodel import Session, create_engine
import app.settings as settings

from collections.abc import Iterator

# Create the engine once globally to avoid recreating the connection pool on every request
engine = create_engine(settings.get_server_settings().database_url)

def get_session() -> Iterator[Session]:
    """Dependency that provides a SQLAlchemy session."""
    with Session(engine) as session:
        yield session