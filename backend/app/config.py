"""Application settings. Values come from the environment / .env file."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Local dev default is SQLite so the project runs with zero setup;
    # Docker Compose overrides this with the Postgres URL.
    database_url: str = "sqlite:///./billmind.db"

    # Week 2: a document at or above this composite confidence auto-drafts its
    # bill; below it, the document goes to the human review queue.
    # Calibrated against the benchmark set — not a number to guess.
    auto_post_threshold: float = 0.85

    upload_dir: str = "uploads"


settings = Settings()
