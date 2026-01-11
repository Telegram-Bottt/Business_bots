import aiosqlite
import os
import glob

def _db_path():
    return os.environ.get('DATABASE_URL', 'sqlite:///./bot.db').replace('sqlite:///', '')

async def init_db():
    files = sorted(glob.glob('migrations/*.sql'))
    async with aiosqlite.connect(_db_path()) as db:
        for p in files:
            with open(p, 'r', encoding='utf-8') as f:
                sql = f.read()
            try:
                await db.executescript(sql)
            except Exception as e:
                msg = str(e).lower()
                # ignore duplicate column errors in Alter migrations
                if 'duplicate column' in msg or 'already exists' in msg:
                    continue
                raise
        await db.commit()

async def get_db():
    conn = await aiosqlite.connect(_db_path())
    conn.row_factory = aiosqlite.Row
    return conn
