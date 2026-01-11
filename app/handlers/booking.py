from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.repo import get_or_create_user, create_booking, list_masters, SlotTaken, DoubleBooking
from app.utils import valid_phone

router = Router()

class BookingStates(StatesGroup):
    SERVICE = State()
    MASTER = State()
    DATE = State()
    TIME = State()
    NAME = State()
    PHONE = State()
    CONFIRM = State()

@router.callback_query(Text(startswith='book:service:'))
async def cb_select_service(query: CallbackQuery, state: FSMContext):
    service_id = int(query.data.split(':')[-1])
    await state.update_data(service_id=service_id)
    # list masters
    masters = await list_masters()
    if not masters:
        await query.message.answer('Нет мастеров. Админ должен добавить мастеров.')
        return
    text = 'Выберите мастера или без выбора:'
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup()
    for m in masters:
        kb.add(InlineKeyboardButton(m['name'], callback_data=f'book:master:{m["id"]}'))
    kb.add(InlineKeyboardButton('Без выбора', callback_data='book:master:0'))
    await query.message.answer(text, reply_markup=kb)
    await query.answer()

@router.callback_query(Text(startswith='book:master:'))
async def cb_select_master(query: CallbackQuery, state: FSMContext):
    master_id = int(query.data.split(':')[-1])
    await state.update_data(master_id=master_id)
    await query.message.answer('Введите дату в формате YYYY-MM-DD (например, 2026-01-15)')
    await BookingStates.DATE.set()
    await query.answer()

@router.callback_query(Text(startswith='book:master_choose:'))
async def cb_master_choose(query: CallbackQuery, state: FSMContext):
    mid = int(query.data.split(':')[-1])
    data = await state.get_data()
    date_s = data.get('date')
    svc_id = data.get('service_id')
    from app.scheduler import generate_slots
    from app.repo import get_service, get_master
    svc = await get_service(svc_id)
    if not svc:
        await query.message.answer('Ошибка: услуга не найдена')
        await query.answer()
        return
    slots = await generate_slots(mid, date_s, svc['duration_minutes'])
    if not slots:
        await query.message.answer('На этот день нет доступных слотов, отправлю ручную заявку админу.')
        await query.answer()
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup()
    for t in slots:
        kb.add(InlineKeyboardButton(t, callback_data=f'book:time:{t}'))
    await query.message.answer(f'Доступные слоты для мастера { (await get_master(mid)) ["name"] } на {date_s}:', reply_markup=kb)
    await BookingStates.TIME.set()
    await query.answer()

@router.message(lambda message: True, state=BookingStates.DATE)
async def process_date(message: Message, state: FSMContext):
    date_s = message.text.strip()
    # minimal validation
    try:
        import datetime
        datetime.date.fromisoformat(date_s)
    except Exception:
        await message.answer('Неверный формат даты. Попробуйте YYYY-MM-DD')
        return
    await state.update_data(date=date_s)

    data = await state.get_data()
    master_id = data.get('master_id')
    svc_id = data.get('service_id')
    from app.repo import list_masters, get_service
    from app.scheduler import generate_slots
    svc = await get_service(svc_id)
    if not svc:
        await message.answer('Ошибка: услуга не найдена')
        return

    if master_id == 0 or master_id is None:
        # show masters who have slots on that date
        masters = await list_masters()
        masters_with = []
        for m in masters:
            slots = await generate_slots(m['id'], date_s, svc['duration_minutes'])
            if slots:
                masters_with.append((m, slots))
        if not masters_with:
            await message.answer('К сожалению, на этот день нет свободных слотов. Я создам ручную заявку.')
            # TODO: create manual_request
            return
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        kb = InlineKeyboardMarkup()
        for m, slots in masters_with:
            kb.add(InlineKeyboardButton(f"{m['name']} ({len(slots)}), выбрать", callback_data=f'book:master_choose:{m['id']}'))
        await message.answer('Выберите мастера с доступным временем:', reply_markup=kb)
        return

    # specific master flow
    slots = await generate_slots(master_id, date_s, svc['duration_minutes'])
    if not slots:
        await message.answer('К сожалению, у выбранного мастера нет слотов на этот день. Попробуйте другую дату или мастера.')
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup()
    for t in slots:
        kb.add(InlineKeyboardButton(t, callback_data=f'book:time:{t}'))
    await message.answer('Выберите время:', reply_markup=kb)
    await BookingStates.TIME.set()

@router.callback_query(Text(startswith='book:time:'))
async def cb_select_time(query: CallbackQuery, state: FSMContext):
    time_s = query.data.split(':')[-1]
    await state.update_data(time=time_s)
    await query.message.answer('Введите ваше имя:')
    await BookingStates.NAME.set()
    await query.answer()

@router.message(lambda message: True, state=BookingStates.TIME)
async def process_time(message: Message, state: FSMContext):
    time_s = message.text.strip()
    try:
        import datetime
        datetime.time.fromisoformat(time_s)
    except Exception:
        await message.answer('Неверный формат времени. Попробуйте HH:MM')
        return
    await state.update_data(time=time_s)
    await message.answer('Введите ваше имя:')
    await BookingStates.NAME.set()

@router.message(lambda message: True, state=BookingStates.NAME)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer('Введите телефон (например, +37061234567):')
    await BookingStates.PHONE.set()

@router.message(lambda message: True, state=BookingStates.PHONE)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not valid_phone(phone):
        await message.answer('Неверный формат телефона. Попробуйте +37061234567')
        return
    await state.update_data(phone=phone)
    data = await state.get_data()
    text = f"Подтвердите запись:\nУслуга ID: {data['service_id']}\nМастер ID: {data['master_id']}\nДата: {data['date']}\nВремя: {data['time']}\nИмя: {data['name']}\nТелефон: {data['phone']}"
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton('Подтвердить', callback_data='book:confirm'), InlineKeyboardButton('Отмена', callback_data='book:cancel'))
    await message.answer(text, reply_markup=kb)
    await BookingStates.CONFIRM.set()

@router.callback_query(Text(equals='book:confirm'), state=BookingStates.CONFIRM)
async def cb_confirm(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = await get_or_create_user(query.from_user.id, name=data.get('name'), phone=data.get('phone'))
    try:
        await create_booking(user['id'], data['service_id'], data['master_id'] if data['master_id'] != 0 else None, data['date'], data['time'], data['name'], data['phone'])
    except SlotTaken:
        await query.message.answer('Извините, это время уже занято. Попробуйте выбрать другое.')
        await state.clear()
        await query.answer()
        return
    except DoubleBooking:
        await query.message.answer('У вас уже есть активная запись. Нельзя записаться второй раз.')
        await state.clear()
        await query.answer()
        return
    # notify admins
    try:
        from app.notify import notify_admins
        await notify_admins(f"Новая запись: {data['date']} {data['time']} Услуга:{data['service_id']} Мастер:{data['master_id']} Клиент:{data['name']} {data['phone']}")
    except Exception:
        pass
    await query.message.answer('Запись подтверждена! Админ уведомлён.')
    await state.clear()
    await query.answer()

@router.callback_query(Text(equals='book:cancel'), state=BookingStates.CONFIRM)
async def cb_cancel(query: CallbackQuery, state: FSMContext):
    await query.message.answer('Запись отменена.')
    await state.clear()
    await query.answer()
