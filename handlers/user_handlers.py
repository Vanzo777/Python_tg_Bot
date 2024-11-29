from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm import state
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext

from config.config import API_TOKEN
from database.database import create_profile, edit_profile, get_profile, get_all_events, delete_event_by_id, \
    get_event_by_id
from filters.filters import IsAdminFilter, IsAdminCallbackFilter
from keyboards.simple_keyboards import create_kb, cancel_kb, main_menu_kb, help_menu_keyboard
from lexicon.lexicon import LEXICON_RU
from aiogram.filters import StateFilter

router = Router()
bot = Bot(API_TOKEN)

class ProfileStatesGroup(StatesGroup):
    photo = State()
    name = State()
    age = State()
    description = State()




@router.message(Command(commands = "start"))
async def process_start_command(message: Message):
    await message.answer(text = LEXICON_RU["/start"],
                         parse_mode='html',
                         reply_markup = create_kb)


@router.message(Command(commands="main_menu"))
async def process_get_main_menu_command(message: Message):
    await message.answer(text = LEXICON_RU["main_menu"], reply_markup=main_menu_kb)



@router.message(lambda message: message.text and message.text.lower() == "помощь")
async def process_help_command(message: Message):
    await message.answer(
        text=LEXICON_RU["/help"],
        parse_mode='html',
        reply_markup=help_menu_keyboard
    )


@router.message(lambda message: message.text and message.text.lower() == "создать анкету")
async def process_create_command(message: Message, state: FSMContext):
    await message.reply(text= LEXICON_RU["/create"],
                        reply_markup= cancel_kb)
    await create_profile(user_id=message.from_user.id, username = message.from_user.username)
    await state.set_state(ProfileStatesGroup.photo)

    # Получаем текущее состояние и выводим его
    # current_state = await state.get_state()
    # print(f"Текущее состояние: {current_state}")  # Печать в консоль


@router.message(lambda message: message.text and message.text.lower() == "отменить создание анкеты")
async def process_cancel(message: Message, state: FSMContext):
     if state is None:
         return
     await state.clear()
     await message.reply(text = LEXICON_RU["/cancel"],
                         reply_markup=create_kb)


@router.message(lambda message: not message.photo, StateFilter(ProfileStatesGroup.photo))
async def process_check_photo(message: Message):
    await message.reply(text=LEXICON_RU["/not_photo"])



@router.message(F.content_type == 'photo', StateFilter(ProfileStatesGroup.photo))
async def process_get_photo(message: Message, state: FSMContext):
    # Сохраняем фото в состояние
    await state.update_data(photo=message.photo[0].file_id)

    # Отправляем ответ и переводим в следующее состояние
    await message.answer('Теперь напишите свое имя:')
    await state.set_state(ProfileStatesGroup.name)

    # Получаем текущее состояние и выводим его
    # current_state = await state.get_state()
    # print(f"Текущее состояние: {current_state}")  # Печать в консоль


@router.message(StateFilter(ProfileStatesGroup.name))
async def process_get_name(message: Message, state: FSMContext):
    # Сохраняем фото в состояние
    await state.update_data(name=message.text)

    # Отправляем ответ и переводим в следующее состояние
    await message.answer('Теперь напишите свой возраст:')
    await state.set_state(ProfileStatesGroup.age)

    # Получаем текущее состояние и выводим его
    # current_state = await state.get_state()
    # print(f"Текущее состояние: {current_state}")  # Печать в консоль

@router.message(StateFilter(ProfileStatesGroup.age))
async def process_get_age(message: Message, state: FSMContext):
    age = message.text

    # Проверяем, является ли введенное значение числом и находится ли в диапазоне
    if age.isdigit() and 16 < int(age) < 99:
        await state.update_data(age=age)
        await message.answer('Отлично!\nТеперь напишите информацию о себе:')
        await state.set_state(ProfileStatesGroup.description)
    else:
        await message.answer('Пожалуйста, введите возраст от 17 до 98 лет, и это должно быть число')

@router.message(StateFilter(ProfileStatesGroup.description))
async def process_get_description(message: Message, state: FSMContext):
    await state.update_data(description = message.text)
    data = await state.get_data()
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=data.get('photo'),
                         caption=f"{data.get('name')}, {data.get('age')}\n{data.get('description')}",
                         reply_markup=main_menu_kb
                         )
    await edit_profile(state, user_id=message.from_user.id)
    await state.clear()


@router.message(lambda message: message.text and message.text.lower() == "моя анкета")
async def process_get_blank(message: Message):
    # Получаем профиль пользователя
    profile = await get_profile(message.from_user.id)

    if profile:
        # Проверяем, заполнены ли все поля
        name, age, photo, description = profile
        if name and age and photo and description:
            # Отправляем анкету пользователю
            await bot.send_photo(chat_id=message.from_user.id,
                                 photo=photo,
                                 caption=f"{name}, {age}\n{description}",
                                 reply_markup=main_menu_kb)
            await bot.send_message(chat_id = message.from_user.id,
                                   text=LEXICON_RU['change_data'])
        else:
            # Если поля не заполнены, просим заполнить анкету
            await message.answer("Ваш профиль не завершен. Пожалуйста, заполните все поля.")
    else:
        # Если профиля нет, просим создать
        await message.answer(text = "Для начала нужно создать анкету.", reply_markup=create_kb)






@router.message(lambda message: message.text and message.text.lower() == "список мероприятий")
async def process_get_events(message: Message):
    events = await get_all_events()  # Предполагаем, что функция возвращает список (id, name)

    if events:
        buttons = [
            [InlineKeyboardButton(text=event_name, callback_data=f"event_{event_id}")]
            for event_id, event_name in events
        ]

        # Если это администратор, добавляем кнопку для удаления
        if await IsAdminFilter()(message):
            buttons.append([InlineKeyboardButton(text="Удалить мероприятие", callback_data="delete_event")])

        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer("Ваши мероприятия:", reply_markup=kb)
    else:
        await message.answer("Нет мероприятий, доступных для отображения.")




@router.callback_query(lambda c: c.data.startswith('event_'))
async def show_event_card(callback: CallbackQuery):
    event_id = callback.data.split('_')[1]  # Извлекаем ID мероприятия
    event = await get_event_by_id(event_id)  # Получаем данные мероприятия

    if event:
        # Формируем текст карточки мероприятия
        card_text = (
            f"<b>{event['event_name']}</b>\n\n"
            f"📅 Начало: {event['date_start']}\n"
            f"📅 Конец: {event['date_end']}\n\n"
            f"{event['event_description']}"
        )

        # Формируем кнопки: ссылка на мероприятие и кнопка "Назад"
        buttons = [
            [InlineKeyboardButton(text="Перейти к мероприятию", url=event['event_url'])],  # Кнопка-ссылка
            [InlineKeyboardButton(text="<- Назад", callback_data="back_to_events")]  # Кнопка "Назад"
        ]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.delete()
        # Отправляем карточку мероприятия с кнопками
        await callback.message.answer_photo(
            photo=event['event_photo'],
            caption=card_text,
            parse_mode='HTML',
            reply_markup=kb
        )
    else:
        await callback.message.answer("Мероприятие не найдено.")

    await callback.answer()


@router.callback_query(lambda c: c.data == "back_to_events")
async def back_to_events(callback: CallbackQuery):
    # Получаем все мероприятия
    events = await get_all_events()  # Предполагаем, что функция возвращает список (id, name)

    if events:
        buttons = [
            [InlineKeyboardButton(text=event_name, callback_data=f"event_{event_id}")]
            for event_id, event_name in events
        ]


        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        # Удаляем старое сообщение и отправляем новое
        await callback.message.delete()
        await callback.message.answer("Ваши мероприятия:", reply_markup=kb)
    else:
        await callback.message.delete()
        await callback.message.answer("Нет мероприятий, доступных для отображения.")




# @router.callback_query(lambda c: c.data.startswith('event_'))
# async def show_event_card(callback: CallbackQuery):
#     event_id = callback.data.split('_')[1]  # Извлекаем ID мероприятия из callback_data
#     event = await get_event_by_id(event_id)  # Функция для получения данных мероприятия по ID
#
#     if event:
#         # Формируем текст карточки мероприятия
#         card_text = (
#             f"<b>{event['event_name']}</b>\n\n"
#             f"📅 Начало: {event['date_start']}\n"
#             f"📅 Конец: {event['date_end']}\n\n"
#             f"{event['event_description']}\n\n"
#             f"<a href='{event['event_url']}'>Перейти к мероприятию</a>"
#         )
#
#         # Отправляем карточку мероприятия
#         await callback.message.answer_photo(
#             photo=event['event_photo'],
#             caption=card_text,
#             parse_mode='HTML'
#         )
#     else:
#         await callback.message.answer("Мероприятие не найдено.")
#
#     # Закрываем callback, чтобы Telegram не показывал "Часы"
#     await callback.answer()
