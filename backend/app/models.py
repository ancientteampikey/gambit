from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class BotProfile(Base):
    __tablename__ = "bot_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    opening: Mapped[str] = mapped_column(String(80), default="Any")
    style: Mapped[str] = mapped_column(String(20), default="balanced")
    elo: Mapped[int] = mapped_column(Integer, default=1500)
    risk: Mapped[int] = mapped_column(Integer, default=50)
    color: Mapped[str] = mapped_column(String(10), default="random")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class GameRecord(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(primary_key=True)
    pgn: Mapped[str] = mapped_column(Text)
    result: Mapped[str] = mapped_column(String(12), default="*")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
