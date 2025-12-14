from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name: str = os.getenv("DATABASE_NAME", "mydb")

    class Config:
        env_file = ".env"


settings = Settings()
client: AsyncIOMotorClient = None
database = None


async def connect_to_mongo():
    """MongoDB 연결"""
    global client, database
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.database_name]
    print("MongoDB 연결 성공")


async def close_mongo_connection():
    """MongoDB 연결 종료"""
    global client
    if client:
        client.close()
        print("MongoDB 연결 종료")


def get_database():
    """데이터베이스 인스턴스 반환"""
    return database

