from pydantic import BaseModel


class Server(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
