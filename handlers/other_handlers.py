from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm import state
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config.config import API_TOKEN
from database.database import create_profile, edit_profile

from keyboards.simple_keyboards import create_kb, cancel_kb
from lexicon.lexicon import LEXICON_RU
from aiogram.filters import StateFilter

router = Router()

@router.message()
async def process_get_age(message: Message, state: FSMContext):
    await message.answer('Извините, я не знаю такой команды'
                         '\nЧтобы узнать, как я работаю, напишите <b>/help</b>', parse_mode='html')
