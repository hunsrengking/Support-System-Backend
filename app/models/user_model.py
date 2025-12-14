from pydantic import BaseModel


class UserModel(BaseModel):
    username: str
    email: str
    password: str
    role_id: int
    department_id: int
    is_locked: int = 0
    failed_attempts: int = 0


class ChangePasswordModel(BaseModel):
    old_password: str
    new_password: str


class LoginRequest(BaseModel):
    email: str
    password: str
