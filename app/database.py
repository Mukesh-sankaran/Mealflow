
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# Read database details from the .env file

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()

# Connect our application to the database
engine = create_engine(
    settings.DATABASE_URL,
    echo=True
)


# Create database sessions whenever we need them
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# All our database tables will be created using this class
class Base(DeclarativeBase):
    pass


# Give API endpoints a database session and close it afterwards
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
