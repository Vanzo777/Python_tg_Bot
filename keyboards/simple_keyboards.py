from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from lexicon.lexicon import LEXICON_RU


#Создаем клавиатуру при помощи билдера
#Первое для создание клавиатуры - создание кнопок
create_button = KeyboardButton(text= 'Создать анкету')
help1_button = KeyboardButton(text = 'Помощь')
cancel_button = KeyboardButton(text = 'Отменить создание анкеты')


create_kb_builder = ReplyKeyboardBuilder()

#После этого в билдер необходимо добавить кнопки при помощи метода row
create_kb_builder.row(create_button, help1_button, width=2)

#После этого необходмо создать клавиатуру с интересующими нас кнопками
create_kb: ReplyKeyboardMarkup = create_kb_builder.as_markup(
    one_time_keyboard = True,
    resize_keyboard = True
)


cancel_kb_builder = ReplyKeyboardBuilder()
cancel_kb_builder.row(cancel_button, width=1)
cancel_kb: ReplyKeyboardMarkup = cancel_kb_builder.as_markup(
    one_time_keyboard = True,
    resize_keyboard = True
)


cancel_event_button = KeyboardButton(text = 'Отменить создание мероприятия')
cancel_event_kb_builder = ReplyKeyboardBuilder()
cancel_event_kb_builder.row(cancel_event_button, width =1)
cancel_event_kb: ReplyKeyboardMarkup = cancel_event_kb_builder.as_markup(
    one_time_keyboard = True,
    resize_keyboard = True
)

#Кнопки для главного меню
events_button = KeyboardButton(text= 'Список мероприятий')
my_blank_button = KeyboardButton(text= 'Моя анкета')
help_button = KeyboardButton(text= 'Помощь')
my_teams_button = KeyboardButton(text= 'Мои команды')


main_menu_kb_builder = ReplyKeyboardBuilder()
#После этого в билдер необходимо добавить кнопки при помощи метода row
main_menu_kb_builder.row(events_button, my_blank_button, help_button, my_teams_button, width=2)
#После этого необходмо создать клавиатуру с интересующими нас кнопками
main_menu_kb: ReplyKeyboardMarkup = main_menu_kb_builder.as_markup(
    one_time_keyboard = True,
    resize_keyboard = True
)

#Кнопки для меню помощи
help_events_button = KeyboardButton(text= 'Список мероприятий')
help_my_blank_button = KeyboardButton(text= 'Моя анкета')
help_my_teams_button = KeyboardButton(text= 'Мои команды')
help_create_button = KeyboardButton(text= 'Создать анкету')

help_menu_keyboard_builder = ReplyKeyboardBuilder()
help_menu_keyboard_builder.row(help_events_button, help_my_teams_button, help_my_blank_button, help_create_button, width=2)
help_menu_keyboard: ReplyKeyboardMarkup = help_menu_keyboard_builder.as_markup(
    one_time_keyboard = True,
    resize_keyboard = True
)

#Кнопки для работы с анкетой
back_to_menu = KeyboardButton(text='1')
change_blank_photo = KeyboardButton(text='2')
change_blank_text = KeyboardButton(text='3')
refield_blank = KeyboardButton(text='4')

blank_keyboard_builder = ReplyKeyboardBuilder()
blank_keyboard_builder.row(back_to_menu, change_blank_photo, change_blank_text, refield_blank, width=4)
blank_keyboard: ReplyKeyboardMarkup = blank_keyboard_builder.as_markup(
    one_time_keyboard = True,
    resize_keyboard = True
)