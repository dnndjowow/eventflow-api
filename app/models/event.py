from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, relationship, mapped_column
from decimal import Decimal
from datetime import datetime

from app.database import Base


class Event(Base):

    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    capacity: Mapped[int] = mapped_column(nullable=False)
    available_seats: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10,2), nullable=False)
    booking_deadline: Mapped[datetime] = mapped_column(nullable=False)
    starts_at: Mapped[datetime] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    bookings: Mapped[list['Booking']] = relationship(
        back_populates='event'
    )