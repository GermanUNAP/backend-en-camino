from pydantic_settings import BaseSettings
from decouple import config

class Settings(BaseSettings):
    project_name: str = "Latam Store API"
    version: str = "1.0.0"
    description: str = "API for Latin America home delivery store with Culqi payments"
    debug: bool = config('DEBUG', default=True, cast=bool)
    
    # Database
    mongo_uri: str = config('MONGO_URI', default='mongodb://localhost:27017/latam_store_db')
    
    # Security
    secret_key: str = config('SECRET_KEY')
    algorithm: str = config('ALGORITHM', default='HS256')
    access_token_expire_minutes: int = config('ACCESS_TOKEN_EXPIRE_MINUTES', default=30, cast=int)
    
    # Culqi
    culqi_public_key: str = config('CULQI_PUBLIC_KEY')
    culqi_secret_key: str = config('CULQI_SECRET_KEY')
    
    # Media
    media_url: str = config('MEDIA_URL', default='/media/')

settings = Settings()