import pytest
from app.db import init_db, get_db
from app.repo import create_master, create_service, get_or_create_user, create_booking, SlotTaken, DoubleBooking
from datetime import date, timedelta


def test_create_entities_and_booking(temp_db):
    async def _run():
        mid = await create_master('Test Master', 'bio', 'contact')
        sid = await create_service('Cut', 'haircut', 10.0, 30)
        user = await get_or_create_user(999999999, 'Test User', '+37061234567')
        d = date.today().isoformat()
        t = '10:00'
        await create_booking(user['id'], sid, mid, d, t, 'Test User', '+37061234567')
        with pytest.raises(DoubleBooking):
            await create_booking(user['id'], sid, mid, d, t, 'Test User', '+37061234567')
    __import__('asyncio').run(_run())


def test_double_booking_prevents_second_booking(temp_db):
    async def _run():
        mid2 = await create_master('Second Master')
        sid2 = await create_service('Wash', 'car wash', 5.0, 30)
        user = await get_or_create_user(111111111, 'UU', '+37061230000')
        d1 = date.today().isoformat()
        t1 = '11:00'
        await create_booking(user['id'], sid2, mid2, d1, t1, 'UU', '+37061230000')
        d2 = (date.today() + timedelta(days=1)).isoformat()
        with pytest.raises(DoubleBooking):
            await create_booking(user['id'], sid2, mid2, d2, '12:00', 'UU', '+37061230000')
    __import__('asyncio').run(_run())


def test_concurrent_slot_booking(temp_db):
    async def _run():
        mid = await create_master('Race Master')
        sid = await create_service('Race Service', 'desc', 10.0, 30)
        user1 = await get_or_create_user(200000001, 'U1', '+37060000001')
        user2 = await get_or_create_user(200000002, 'U2', '+37060000002')
        d = date.today().isoformat()
        t = '14:00'

        async def try_book(user):
            try:
                await create_booking(user['id'], sid, mid, d, t, user['name'], user['phone'])
                return 'ok'
            except SlotTaken:
                return 'taken'
            except DoubleBooking:
                return 'double'

        import asyncio as _async
        r = await _async.gather(try_book(user1), try_book(user2))
        assert r.count('ok') == 1
        assert r.count('taken') + r.count('double') == 1
    __import__('asyncio').run(_run())
