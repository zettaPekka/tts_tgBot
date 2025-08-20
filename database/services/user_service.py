from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repositories.user_repo import UserRepo


class UserService:
    def __init__(self, session: AsyncSession, user_repo: UserRepo):
        self.session = session
        self.user_repo = user_repo
    
    async def create_if_not_exists(self, tg_id: int):
        user = await self.user_repo.get(tg_id)
        if not user:
            user = await self.user_repo.add(tg_id)
            await self.session.commit()
            await self.session.refresh(user)
        return user
        
    
    async def get(self, tg_id: int):
        return await self.user_repo.get(tg_id)

    async def update_balance(self, tg_id: int, amount: int):
        await self.user_repo.update_balance(tg_id, amount)
        await self.session.commit()
    
    async def set_user_voice(self, tg_id: int, voice_id: str):
        await self.user_repo.set_user_voice(tg_id, voice_id)
        await self.session.commit()
    
    async def get_all(self):
        return await self.user_repo.get_all()
