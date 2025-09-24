from src.kit.schemas import IDSchema, Schema


class BaseUser(Schema):
    first_name: str
    last_name: str | None
    username: str | None


class UserCreate(IDSchema, BaseUser):
    is_premium: bool = False


class UserRead(BaseUser):
    balance: float


class PanelUserRead(BaseUser):
    id: int
    balance: float
    api_key: str


class RevokeTokenResponse(Schema):
    success: bool
    api_key: str
