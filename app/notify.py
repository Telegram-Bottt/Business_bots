import os
from aiogram import Bot

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_IDS = [int(x) for x in os.environ.get('ADMIN_IDS','').split(',') if x]

async def notify_admins(text: str):
    if not BOT_TOKEN or not ADMIN_IDS:
        return
    bot = Bot(BOT_TOKEN)
    try:
        for aid in ADMIN_IDS:
            try:
                await bot.send_message(aid, text)
            except Exception:
                # ignore send errors
                pass
    finally:
        await bot.session.close()
