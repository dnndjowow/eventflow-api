from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String

from app.database import Base

class User(Base):

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    bookings: Mapped[list['Booking']] = relationship(
        back_populates='user'
    )