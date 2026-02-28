"""應用程式組態：集中管理所有環境變數與設定值。"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """從環境變數讀取的應用程式設定。"""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/apexmath"

    # JWT
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 480  # 8 hours
    jwt_student_token_expire_minutes: int = 180  # 3 hours

    # CORS
    cors_origins: str = "*"

    # OpenAI
    openai_api_key: str | None = None

    # Admin seed
    admin_username: str = "admin"
    admin_password: str = "changeme"

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def async_database_url(self) -> str:
        """回傳 asyncpg 相容的連線字串。Render 提供 postgres:// 前綴需要轉換。"""
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


settings = Settings()
