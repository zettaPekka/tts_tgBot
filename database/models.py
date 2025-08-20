from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import BigInteger


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    voice: Mapped[str] = mapped_column(nullable=True)
    balance: Mapped[int] = mapped_column(default=0)