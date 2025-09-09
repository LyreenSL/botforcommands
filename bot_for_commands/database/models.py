from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm.properties import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import BigInteger, String, UniqueConstraint
from typing import TypeVar


class Base(AsyncAttrs, DeclarativeBase):
    pass


TBase = type[TypeVar('T', bound=Base)]


class Chat(Base):
    __tablename__ = 'chats'
    id: Mapped[BigInteger] = mapped_column(BigInteger(), primary_key=True, unique=True)

    members_rights: Mapped[bool] = mapped_column(default=True)
    welcome_message: Mapped[str | None] = mapped_column(String(4100))

    triggers: Mapped[list['Trigger']] = relationship(
        back_populates='chat',
        lazy='subquery',
        cascade='all, delete-orphan',
    )
    actions: Mapped[list['Action']] = relationship(
        back_populates='chat',
        lazy='subquery',
        cascade='all, delete-orphan',
    )


class Trigger(Base):
    __tablename__ = 'triggers'
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)

    word: Mapped[str] = mapped_column(String(4096))
    answer: Mapped[str] = mapped_column(String(4096))

    chat: Mapped['Chat'] = relationship(back_populates='triggers')
    chat_id: Mapped[int] = mapped_column(
        ForeignKey('chats.id', ondelete='cascade')
    )

    __table_args__ = (UniqueConstraint('chat_id', 'word', name='unique_word_for_chat'),)


class Action(Base):
    __tablename__ = 'actions'
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)

    is_interaction: Mapped[bool]
    command: Mapped[str] = mapped_column(String(4096))
    text: Mapped[str] = mapped_column(String(4096))

    chat: Mapped['Chat'] = relationship(back_populates='actions')
    chat_id: Mapped[int] = mapped_column(
        ForeignKey('chats.id', ondelete='cascade')
    )

    __table_args__ = (UniqueConstraint('chat_id', 'command', name='unique_command_for_chat'),)

