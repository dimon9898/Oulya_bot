from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import SecretStr, computed_field, field_validator


class Settings(BaseSettings):
    MAX_TOKEN: str
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    LOGO_ID: str
    CHANEL_LINK: str
    CHANEL_ID: int
    SHOP_ID: int
    SHOP_SECRET_KEY: SecretStr
    WEBHOOK_URL: str
    SECRET_MAX: str
    ADMIN_IDS: str


    @computed_field
    @property
    def get_db_url(self) -> str:
        return (f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD.get_secret_value()}'
                f'@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}')
    
    
    @field_validator('ADMIN_IDS', mode='after')
    @classmethod
    def list_admins(cls, value: str) -> list[int]:
        return [int(admin_id.strip()) for admin_id in value.split(',')]


    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()

print(settings.ADMIN_IDS)