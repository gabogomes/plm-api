from typing import Optional, Any
from pydantic import BaseSettings


class PlmSettings(BaseSettings):
    db_name: str
    db_username: str
    db_password: Optional[str]
    local_db_host: Optional[str]
    local_db_port: Optional[int]
