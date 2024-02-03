from pydantic import BaseSettings


class PlmSettings(BaseSettings):
    db_name: str
    db_username: str
    plm_email_address: str
    plm_email_password: str
    smtp_server: str
    smtp_port: int
    db_password: str
    local_db_host: str
    local_db_port: int
