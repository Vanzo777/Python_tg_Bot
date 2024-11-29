from aiogram.filters import BaseFilter
from aiogram.types import Message
from config.config import ADMIN_ID
from aiogram.types import Message, CallbackQuery
from typing import Union

class IsAdminMessageFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == ADMIN_ID


class IsAdminCallbackFilter(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.from_user.id == ADMIN_ID


class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == ADMIN_ID
