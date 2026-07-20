from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid7

from sqlalchemy import DateTime, Float, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from brookie.models.base import Base

if TYPE_CHECKING:
    from brookie.models.session import Session


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    location: Mapped[str] = mapped_column(String)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(String)

    sessions: Mapped[list["Session"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )
