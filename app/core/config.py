from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Event Management CRM"
    API_V1_STR: str = "/api/v1"

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION_NAME: str = "ap-southeast-1"
    DYNAMODB_TABLE_PREFIX: str = "EventCRM"

    SENDGRID_API_KEY: str
    SENDGRID_SENDER_EMAIL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()