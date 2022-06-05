from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    __slots__ = ("login", "password", "email")
    login: str
    password: str
    email: str

    @property
    def outer_api_interface(self) -> dict:
        return {
            "username": self.login,
            "password": self.password,
            "email": self.email,
        }

    @property
    def login_info(self) -> dict:
        return {
            "username": self.login,
            "password": self.password,
        }

    @property
    def sql_interface(self) -> dict:
        return {"login": self.login, "password": self.password, "email": self.email}


@dataclass(frozen=True)
class LoginUsers(User):
    token_1: str
    token_2: str
