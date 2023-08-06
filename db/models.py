from datetime import date

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, DATE, INTEGER

from db.base import Base


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100))
    fullname: Mapped[str] = mapped_column(String(100))

    def __str__(self):
        return f'User {self.username}: {self.user_id}'


class MentalState(Base):
    __tablename__ = 'states'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(ForeignKey('users.user_id'))
    date: Mapped[date] = mapped_column(DATE, default=date.today())
    state: Mapped[int] = mapped_column(INTEGER)
