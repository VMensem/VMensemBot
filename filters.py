from aiogram import types
from aiogram.filters import BaseFilter
from config import CREATOR_ID
from data_manager import DataManager

class IsAdmin(BaseFilter):
    """Filter for checking if user is admin."""
    def __init__(self, *args, **kwargs):
        self.is_admin = True

    async def __call__(self, message: types.Message) -> bool:
        data_manager = DataManager()
        admins = data_manager.get_admins()  # список админов

        user_id_str = str(message.from_user.id)

        # Поддержка обеих форм: list[int] или dict[str, username]
        if isinstance(admins, list):
            return message.from_user.id in admins or message.from_user.id == CREATOR_ID
        elif isinstance(admins, dict):
            return user_id_str in admins or message.from_user.id == CREATOR_ID

        return False

class IsCreator(BaseFilter):
    """Filter for checking if user is creator."""
    def __init__(self, *args, **kwargs):
        self.is_creator = True

    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id == CREATOR_ID
