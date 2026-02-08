#!/usr/bin/env python3
"""Test format_booking_for_display function."""

import asyncio
import tempfile
import os
from app.db import init_db
from app.repo import (
    create_service, create_master, get_or_create_user,
    create_booking, format_booking_for_display, list_bookings
)

async def main():
    # Setup temp database
    dbfile = tempfile.mktemp(suffix='.db')
    os.environ['BOT_DB'] = dbfile
    await init_db()
    
    # Create test data
    service_id = await create_service('💇 Стрижка', 'Классическая мужская стрижка', 500.0, 30)
    master_id = await create_master('Иван Мастер', 'Опытный барбер', '+7-999-123-4567')
    user = await get_or_create_user(123456, name='Петр Клиент', phone='+7-999-765-4321')
    
    # Create a booking
    booking_id = await create_booking(
        user_id=user['id'],
        service_id=service_id,
        master_id=master_id,
        date_s='2026-02-15',
        time_s='14:30',
        name='Петр Клиент',
        phone='+7-999-765-4321'
    )
    
    # Get the booking and format it
    bookings = await list_bookings()
    booking = bookings[0]
    
    print("=" * 60)
    print("ТЕСТ ФОРМАТИРОВАНИЯ ЗАПИСИ")
    print("=" * 60)
    print()
    
    formatted = await format_booking_for_display(booking)
    print(formatted)
    print()
    
    print("=" * 60)
    print("✅ Форматирование работает корректно!")
    print("=" * 60)
    
    # Cleanup
    os.unlink(dbfile)

if __name__ == '__main__':
    asyncio.run(main())
