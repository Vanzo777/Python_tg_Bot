from aiogram import Router, F, Bot
from aiogram.filters import Command, BaseFilter
from aiogram.fsm import state
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from config.config import API_TOKEN, ADMIN_ID
from database.database import create_event, edit_event, clear_table, get_all_events, delete_event_by_id
from filters.filters import IsAdminFilter
from keyboards.simple_keyboards import create_kb, cancel_kb, main_menu_kb, cancel_event_kb
from lexicon.lexicon import LEXICON_RU
from aiogram.filters import StateFilter
from datetime import datetime

router = Router()
bot = Bot(API_TOKEN)



router.message.filter(IsAdminFilter())

class EventStatesGroup(StatesGroup):
    event_photo = State()
    event_name = State()
    date_start = State()
    date_end = State()
    event_description = State()
    event_url = State()


@router.message(Command(commands='add_event'))
async def process_add_event(message: Message, state: FSMContext):
    await message.reply(text= LEXICON_RU["/create_event"],
                        reply_markup= cancel_event_kb)
    event_id = await create_event()
    await state.update_data(event_id=event_id)
    await state.set_state(EventStatesGroup.event_name)


@router.message(lambda message: message.text and message.text.lower() == "отменить создание мероприятия")
async def process_cancel_event(message: Message, state: FSMContext):
     if state is None:
         return
     await state.clear()
     await message.reply(text = LEXICON_RU["/cancel_event"],
                         reply_markup=main_menu_kb)
     await clear_table()

@router.message(StateFilter(EventStatesGroup.event_name))
async def process_get_event_name(message: Message, state: FSMContext):
    await state.update_data(event_name = message.text)
    await message.answer('Неплохое название! Теперь напиши дату начала мероприятия в формате ДД-ММ-ГГГГ')
    await state.set_state(EventStatesGroup.date_start)





@router.message(StateFilter(EventStatesGroup.date_start))
async def process_get_date_start(message: Message, state: FSMContext):
    date_format_input = "%d-%m-%Y"  # Формат для ввода даты ДД-ММ-ГГГГ
    date_format_db = "%d.%m.%Y"      # Формат для сохранения в БД ДД.ММ.ГГГГ

    try:
        # Преобразуем введенную строку в объект даты
        entered_date = datetime.strptime(message.text, date_format_input)
        current_date = datetime.now()

        # Проверяем, что введенная дата не позднее текущей
        if entered_date >= current_date:
            # Преобразуем дату в нужный формат для БД
            formatted_date = entered_date.strftime(date_format_db)
            # Сохраняем дату начала в состоянии, если проверка пройдена
            await state.update_data(date_start=formatted_date)
            await message.answer('Отлично!\nТеперь напишите дату окончания в формате ДД-ММ-ГГГГ:')
            await state.set_state(EventStatesGroup.date_end)
        else:
            # Сообщаем, если дата раньше текущей
            await message.answer('Дата начала мероприятия не может быть раньше сегодняшней. Введите правильную дату:')
    except ValueError:
        # Обрабатываем ошибку, если дата не соответствует формату
        await message.answer('Неверный формат даты. Пожалуйста, введите дату в формате ДД-ММ-ГГГГ.')



@router.message(StateFilter(EventStatesGroup.date_end))
async def process_get_date_end(message: Message, state: FSMContext):
    date_format_input = "%d-%m-%Y"  # Формат для ввода даты ДД-ММ-ГГГГ
    date_format_db = "%d.%m.%Y"      # Формат для сохранения в БД ДД.ММ.ГГГГ

    data = await state.get_data()  # Получаем данные из состояния

    try:
        # Преобразуем введенную строку в объект даты
        entered_date = datetime.strptime(message.text, date_format_input)
        start_date = datetime.strptime(data.get('date_start'), date_format_db)  # Получаем дату начала

        # Проверяем, что введенная дата не раньше даты начала
        if entered_date >= start_date:
            # Преобразуем дату в нужный формат для БД
            formatted_date = entered_date.strftime(date_format_db)
            # Сохраняем дату окончания в состоянии, если проверка пройдена
            await state.update_data(date_end=formatted_date)
            await message.answer('Отлично!\nТеперь опишите мероприятие:')
            await state.set_state(EventStatesGroup.event_description)
        else:
            # Сообщаем, если дата окончания раньше даты начала
            await message.answer('Дата окончания мероприятия не может быть раньше даты начала. Введите правильную дату:')
    except ValueError:
        # Обрабатываем ошибку, если дата не соответствует формату
        await message.answer('Неверный формат даты. Пожалуйста, введите дату в формате ДД-ММ-ГГГГ.')



@router.message(StateFilter(EventStatesGroup.event_description))
async def process_get_event_name(message: Message, state: FSMContext):
    await state.update_data(event_description = message.text)
    await message.answer('Осталось совсем чуть-чуть, теперь загрузи обложку мероприятия:')
    await state.set_state(EventStatesGroup.event_photo)




@router.message(lambda message: not message.photo, StateFilter(EventStatesGroup.event_photo))
async def process_check_event_photo(message: Message):
    await message.reply(text=LEXICON_RU["/not_photo"])



@router.message(F.content_type == 'photo', StateFilter(EventStatesGroup.event_photo))
async def process_get_event_photo(message: Message, state: FSMContext):
    # Сохраняем фото в состояние
    await state.update_data(event_photo=message.photo[0].file_id)

    # Отправляем ответ и переводим в следующее состояние
    await message.answer('Супер! Осталось только отправить ссылку на мероприятие:')
    await state.set_state(EventStatesGroup.event_url)



### - Доделать обработчик для получения ссылку на форму и вывода мероприятия
@router.message(StateFilter(EventStatesGroup.event_url))
async def process_get_event_url(message: Message, state: FSMContext):
    await state.update_data(event_url = message.text)
    data = await state.get_data()
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=data.get('event_photo'),
                         caption=f"{data.get('date_start')}-{data.get('date_end')},{data.get('event_name')}\n{data.get('event_description')}",
                         reply_markup=main_menu_kb
                         )

    await edit_event(state)
    await state.clear()
###


@router.callback_query(lambda c: c.data == "delete_event" and IsAdminFilter()(c.message))
async def process_delete_event_request(callback_query: CallbackQuery):
    events = await get_all_events()  # Предполагаем, что функция возвращает список (id, name)

    if events:
        buttons = [
            [InlineKeyboardButton(text=f"X {event_name}", callback_data=f"delete_{event_id}")]
            for event_id, event_name in events
        ]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback_query.message.answer("Выберите мероприятие для удаления:", reply_markup=kb)
    else:
        await callback_query.message.answer("Нет мероприятий, доступных для удаления.")


@router.callback_query(lambda c: c.data.startswith("delete_") and IsAdminFilter()(c.message))
async def process_delete_event(callback_query: CallbackQuery):
    event_id = callback_query.data.split("_")[1]

    # Логика для удаления мероприятия из базы
    await delete_event_by_id(event_id)

    await callback_query.message.answer(f"Мероприятие с ID {event_id} удалено.")


