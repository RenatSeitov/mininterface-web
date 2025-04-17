from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import BaseModel, field_validator
from pydantic import model_validator


class Url(BaseModel):
    url: Optional[str] = None


class Settings(BaseSettings):
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "register_map_db"
    postgres_user: str = "register_maps_api"
    postgres_password: str = "register_maps_api"
    postgres_database_url: Url = Url()
    
    @field_validator('postgres_database_url', mode='before')
    def parse_db_url(cls, v):
        if isinstance(v, str):
            return {"url": v}
        if isinstance(v, dict):
            return v
        return Url()

settings = Settings()
print(settings.postgres_database_url.url)