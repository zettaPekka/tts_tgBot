from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import User


class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add(self, tg_id: int):
        user = User(tg_id=tg_id)
        self.session.add(user)
        return user
    
    async def get(self, tg_id: int):
        return await self.session.get(User, tg_id)

    async def update_balance(self, tg_id: int, amount: int):
        user = await self.get(tg_id)
        user.balance += amount

    async def set_user_voice(self, tg_id: int, voice_id: str):
        user = await self.get(tg_id)
        user.voice = voice_id
    
    async def get_all(self):
        users = await self.session.execute(select(User))
        users = users.scalars().all()
        return users
