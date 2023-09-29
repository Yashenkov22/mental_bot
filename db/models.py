from datetime import date

from sqlalchemy import String, ForeignKey, DATE, INTEGER
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(100))
    subscription: Mapped[bool] = mapped_column(default=True)


class MentalState(Base):
    __tablename__ = 'states'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id = mapped_column(ForeignKey('users.user_id'))
    date: Mapped[date] = mapped_column(DATE, default=date.today())
    state: Mapped[int] = mapped_column(INTEGER)


class Picture(Base):
    __tablename__ = 'pictures'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pic_id: Mapped[str]
    user_id = mapped_column(ForeignKey('users.user_id'))