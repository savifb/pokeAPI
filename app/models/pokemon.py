from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from app.database import Base




class Pokemon(Base):
    __tablename__ = 'Pokemon'
    id: Mapped[int] = mapped_column(Integer, index=True, primary_key=True) 
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    weight: Mapped[int] = mapped_column(Integer, nullable=False)
    types: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    sprite_front: Mapped[str|None] = mapped_column(String, nullable=True)
    sprite_back: Mapped[str|None] = mapped_column(String, nullable=True)
    tempo_cache: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), nullable=False)


def __repr__(self):# quando fazer o print - ele fica legível - mostrando id e o nome do pokemon
        return f"<Pokemon id={self.id} name={self.name}>"
    
