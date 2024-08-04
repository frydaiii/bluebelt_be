from sqlalchemy import create_engine
from sqlalchemy.orm import Session, DeclarativeBase
from datetime import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import Column, Integer, String, DateTime


class Base(DeclarativeBase):
    pass


class Chat(Base):
    __tablename__ = "chat"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    timezone: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return f"<Chat(id={self.id}, client_id={self.client_id}, created_at={self.created_at})>"


class Message(Base):
    __tablename__ = "message"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime)

    def __repr__(self):
        return f"<Message(id={self.id}, chat_id={self.chat_id}, content={self.content}, created_at={self.created_at})>"


class DB:

    def __init__(self, address: str = "sqlite:///local.db"):
        self.__engine = create_engine(address, echo=True)
        Base.metadata.create_all(self.__engine, checkfirst=True)
        self.__session = Session(self.__engine)

    def get_chat(self, client_id: int):
        return self.__session.query(Chat).filter_by(client_id=client_id).first()

    def create_chat(self, client_id: int, timezone: str):
        chat = Chat(client_id=client_id,
                    created_at=datetime.now(),
                    timezone=timezone)
        self.__session.add(chat)
        self.__session.commit()
        return chat

    def create_message(self, chat_id: int, content: str):
        message = Message(chat_id=chat_id,
                          content=content,
                          created_at=datetime.now())
        self.__session.add(message)
        self.__session.commit()
        return message
