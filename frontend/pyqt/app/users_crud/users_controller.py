

from app.api_client.users_api_client import UsersApiClient
from app.users_crud.users_view import UsersView
from app.models.generated_models import RolePublic, UserCreate, UserPublic
from app.api_client.roles_api_client import RolesApiClient
from app.api_client.base_api_client_factory import get_base_client
from PyQt6 import QtWidgets, QtCore

class UsersController(QtCore.QObject):
    LOAD_ROLES = "load_roles"
    LOAD_USERS = "load_users"
    def __init__(self, view: UsersView):
        super().__init__()
        self.view = view

        self.users:list[UserPublic] = []
        base_api_client = get_base_client()

        self.roles_api_client = RolesApiClient(base_api_client)
        self.roles_api_client.get_roles_success.connect(self._on_roles_loaded)
        self.roles_api_client.get_roles_error.connect(lambda error: print(f"Error loading roles: {error}"))

        self.users_api_client = UsersApiClient(base_api_client)
        self.users_api_client.get_all_users_success.connect(self._on_users_loaded)
        self.users_api_client.get_all_users_error.connect(lambda error: print(f"Error loading users: {error}"))
        self.users_api_client.register_error.connect(lambda error: print(f"Error registering user: {error}"))
        self.users_api_client.update_user_error.connect(lambda error: print(f"Error updating user: {error}"))
        self.users_api_client.delete_user_error.connect(lambda error: print(f"Error deleting user: {error}"))


        self.view.save_btn.clicked.connect(self.save_users)
        self.view.create_blank_user.connect(self.create_blank_user)

        self.tasks:list[str] = [self.LOAD_ROLES, self.LOAD_USERS]
        # Load available roles to populate the dropdowns and then load users
        self.get_available_roles()
        self.get_users()


    def get_available_roles(self):
        self.roles_api_client.get_roles()


    def _on_roles_loaded(self, roles:list[RolePublic]):
        self.view.available_roles = {role.id: role.name for role in roles if role.id is not None}
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
        self.view.add_user_row(user_id=-1, email="", name="", role_id=None)

    def is_blank_user(self, user_data:tuple[int, str, str, int, str]) -> bool:
        user_id, email, name, role_id, password = user_data
        return user_id == -1 and email == "" and name == "" and password == "" and role_id == None

    def load_users(self, users:list[UserPublic]):
        self.view.table.setRowCount(0)  # Clear existing rows
        for user in users:
            self.view.add_user_row(user_id=user.id, email=user.email, name=user.name, role_id=user.role_id)

    def _minimum_comprobations(self, user:UserCreate, new_user:bool=True) -> bool:
        """Make small comprobations to create the user"""
        if not user.email or '@' not in user.email:
            return False
        if not user.name:
            return False
        if new_user and not user.password:
            return False
        if user.role_id not in self.view.available_roles:
            return False
        return True
    
    def check_users(self, users_data:list[tuple[int, str, str, int, str, int]]) -> bool:
        """Check if the users in the view are correct"""
        for data in users_data:
            if self.is_blank_user(data[0:5]):
                continue #Skip blank users

            user = UserCreate(name=data[2], email=data[1], password=data[4], role_id=data[3])

            if data[0] == -1:  # New user
                if not self._minimum_comprobations(user, new_user=True):
                    print(f"Validation failed for new user: {user}")
                    self.view.show_tooltip_error_in_a_row(data[5], "Invalid user data. Please check the email format, ensure name and password are not empty, and select a valid role.")
                    return False
            else:  # Existing user
                if not self._minimum_comprobations(user, new_user=False):
                    print(f"Validation failed for existing user: {user}")
                    self.view.show_tooltip_error_in_a_row(data[5], "Invalid user data. Please check the email format, ensure name is not empty, and select a valid role.")
                    return False    
        return True

    def save_users(self):
        """Extract data from the view and determine which users to create, update, or delete."""
        user_data = self.view.get_data()
       
        if not self.check_users(user_data):
            print("User data validation failed. Aborting save operation.")
            return
        
        for data in user_data:
            if self.is_blank_user(data[0:5]):
                continue #Skip blank users

            if data[0] == -1:  # New user (user_id == -1)
                self.users_api_client.register(UserCreate(name=data[2], email=data[1], password=data[4], role_id=data[3]))

            for i in self.users:
                if i.id == data[0]: #Existing user, check for updates
                    if i.email != data[1] or i.name != data[2] or i.role_id != data[3]:
                        self.users_api_client.update_user(i.id, UserCreate(name=data[2], email=data[1], password=data[4], role_id=data[3]))
                    self.users.remove(i) #Remove from the list to keep track of deleted users
                    break
            
        for user in self.users:
            self.users_api_client.delete_user(user.id)
        
        QtWidgets.QMessageBox.information(self.view, self.view.tr("Success"), self.view.tr("Users saved successfully."))
        self.view.accept()