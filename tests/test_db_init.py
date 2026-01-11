import asyncio
from app.db import init_db, get_db

def test_init_db():
    asyncio.run(_test())

async def _test():
    await init_db()
    db = await get_db()
    cur = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bookings'")
    row = await cur.fetchone()
    assert row is not None
    await db.close()

if __name__ == '__main__':
    asyncio.run(_test())
