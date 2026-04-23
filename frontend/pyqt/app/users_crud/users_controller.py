

from frontend.pyqt.app.api_client.users_api_client import UsersApiClient
from frontend.pyqt.app.users_crud.users_view import UsersView
from frontend.pyqt.app.models.generated_models import RolePublic, UserPublic
from frontend.pyqt.app.api_client.roles_api_client import RolesApiClient
from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client

class UsersController:
    LOAD_ROLES = "load_roles"
    LOAD_USERS = "load_users"
    def __init__(self, view: UsersView):
        self.view = view

        self.users:list[UserPublic] = []
        base_api_client = get_base_client()

        self.roles_api_client = RolesApiClient(base_api_client)
        self.roles_api_client.get_roles_success.connect(self._on_roles_loaded)
        self.roles_api_client.get_roles_error.connect(lambda error: print(f"Error loading roles: {error}"))

        self.users_api_client = UsersApiClient(base_api_client)
        self.users_api_client.get_all_users_success.connect(self._on_users_loaded)
        self.users_api_client.get_all_users_error.connect(lambda error: print(f"Error loading users: {error}"))

        self.view.save_btn.clicked.connect(self.save_users)
        self.view.create_blank_user.connect(self.create_blank_user)

        self.tasks:list[str] = [self.LOAD_ROLES, self.LOAD_USERS]
        # Load available roles to populate the dropdowns and then load users
        self.get_available_roles()
        self.get_users()


    def get_available_roles(self):
        self.roles_api_client.get_roles()


    def _on_roles_loaded(self, roles:list[RolePublic]):
        self.view.available_roles = {role.id: role.name for role in roles}
        self._on_ready_to_display(self.LOAD_ROLES)


    def get_users(self):
        self.users_api_client.get_all_users()


    def _on_users_loaded(self, users:list[UserPublic]):
        self.users = users
        self._on_ready_to_display(self.LOAD_USERS)


    def _on_ready_to_display(self, caller:str):
        self.tasks.remove(caller)
        if not self.tasks:
            self.load_users(self.users)

    def create_blank_user(self):
        self.view.add_user_row(user_id=-1, email="", name="", role_id=-1)

    def load_users(self, users:list[UserPublic]):
        self.view.table.setRowCount(0)  # Clear existing rows
        for user in users:
            self.view.add_user_row(user_id=user.id, email=user.email, name=user.name, role_id=user.role_id)


    def save_users(self):
        user_data = self.view.get_data()
        # Here you would typically send this data to your backend or service layer
        print("Saving users:", user_data)