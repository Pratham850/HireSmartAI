import os
from dotenv import load_dotenv

# Load .env file automatically
load_dotenv()

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    
    class Settings(BaseSettings):
        PROJECT_NAME: str = os.getenv("PROJECT_NAME", "HireSmart AI - Campus Recruitment Automation System")
        VERSION: str = os.getenv("VERSION", "1.0.0")
        DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

        # Database
        DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+aiomysql://root:password@localhost:3306/hiresmart_db")

        # JWT Security
        SECRET_KEY: str = os.getenv("SECRET_KEY", "hiresmart_ai_super_secret_jwt_key_campus_recruitment_2026")
        ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
        ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

        # Groq AI
        GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
        MODEL: str = os.getenv("MODEL", "llama-3.3-70b-versatile")

        # Sentence Transformers Embedding
        EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

        # Directories
        UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
        PDF_DIR: str = os.getenv("PDF_DIR", "uploads/pdf")
        JSON_DIR: str = os.getenv("JSON_DIR", "uploads/json")
        REPORT_DIR: str = os.getenv("REPORT_DIR", "reports")

        # SMTP Email Settings
        SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
        SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
        SMTP_USER: str = os.getenv("SMTP_USER", "")
        SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
        EMAIL_FROM: str = os.getenv("EMAIL_FROM", "recruitment@hiresmart.ai")

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore"
        )

except ImportError:
    # Lightweight dataclass/object fallback if pydantic-settings is not installed in the python env
    class Settings:
        PROJECT_NAME: str = os.getenv("PROJECT_NAME", "HireSmart AI - Campus Recruitment Automation System")
        VERSION: str = os.getenv("VERSION", "1.0.0")
        DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

        DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+aiomysql://root:password@localhost:3306/hiresmart_db")

        SECRET_KEY: str = os.getenv("SECRET_KEY", "hiresmart_ai_super_secret_jwt_key_campus_recruitment_2026")
        ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
        ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

        GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
        MODEL: str = os.getenv("MODEL", "llama-3.3-70b-versatile")

        EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

        UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
        PDF_DIR: str = os.getenv("PDF_DIR", "uploads/pdf")
        JSON_DIR: str = os.getenv("JSON_DIR", "uploads/json")
        REPORT_DIR: str = os.getenv("REPORT_DIR", "reports")

        SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
        SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
        SMTP_USER: str = os.getenv("SMTP_USER", "")
        SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
        EMAIL_FROM: str = os.getenv("EMAIL_FROM", "recruitment@hiresmart.ai")


settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PDF_DIR, exist_ok=True)
os.makedirs(settings.JSON_DIR, exist_ok=True)
os.makedirs(settings.REPORT_DIR, exist_ok=True)
