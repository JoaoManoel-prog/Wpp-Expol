from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    VERIFY_TOKEN: str = Field(..., description="Token para verificação do Webhook")
    APP_SECRET: str = Field(..., description="App Secret da Meta para assinatura HMAC")
    WHATSAPP_TOKEN: str = Field(..., description="Long-lived Access Token")
    PHONE_NUMBER_ID: str = Field(..., description="Phone Number ID do WhatsApp Business")

    JWT_SECRET: str = Field(...)
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 dias
    ENV: str = "dev"

    DATABASE_URL: str = "sqlite:///./data.db"

    class Config:
        env_file = ".env"

settings = Settings()
