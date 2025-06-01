from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from database.session import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=True)
    telegram_id = Column(Integer, unique=True)
    role = Column(Enum('user', 'support', 'admin'))  # Роли пользователей

class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    description = Column(String(500))
    status = Column(Enum('open', 'in_progress', 'closed'))
    created_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))
