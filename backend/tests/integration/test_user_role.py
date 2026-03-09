import pytest
from sqlmodel import Session, SQLModel, create_engine
from backend.app.models.user import User
from backend.app.models.role import Role

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_user_role_relationship(session: Session):
    # 1. Create a Role
    admin_role = Role(name="Admin")
    session.add(admin_role)
    session.commit()
    session.refresh(admin_role)

    # 2. Create a User associated with that Role
    user = User(
        name="Admin User", 
        email="admin@example.com", 
        password_hash="hash",
        role_id=admin_role.id
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # 3. Assert going from User -> Role works
    assert user.role is not None
    assert user.role.name == "Admin"
    assert user.role.id == admin_role.id

    # 4. Assert going from Role -> User (back_populates) works
    # We must refresh the role to load the relationship data from the db
    session.refresh(admin_role)
    assert len(admin_role.users) == 1
    assert admin_role.users[0].name == "Admin User"
    assert admin_role.users[0].email == "admin@example.com"

def test_multiple_users_per_role(session: Session):
    # 1. Create a Role
    editor_role = Role(name="Editor")
    session.add(editor_role)
    session.commit()
    session.refresh(editor_role)

    # 2. Create multiple Users with the same Role
    user1 = User(name="Ed 1", email="ed1@example.com", password_hash="hash", role_id=editor_role.id)
    user2 = User(name="Ed 2", email="ed2@example.com", password_hash="hash", role_id=editor_role.id)
    
    session.add_all([user1, user2])
    session.commit()

    # 3. Verify the Role has exactly 2 users inside `editor_role.users`
    session.refresh(editor_role)
    assert len(editor_role.users) == 2
    assert {u.name for u in editor_role.users} == {"Ed 1", "Ed 2"}

def test_user_without_role(session: Session):
    # Verify a user can be created without a role (it's optional)
    free_user = User(name="Free", email="free@example.com", password_hash="hash")
    session.add(free_user)
    session.commit()
    session.refresh(free_user)
    
    assert free_user.role_id is None
    assert free_user.role is None