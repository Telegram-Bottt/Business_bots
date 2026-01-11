import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

from app.bot import start_bot

if __name__ == '__main__':
    asyncio.run(start_bot())
