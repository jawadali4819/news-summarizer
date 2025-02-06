# db.py
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import logging
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

client = AsyncIOMotorClient(MONGODB_URI)
db_name = "news_article"
db = client[db_name]
