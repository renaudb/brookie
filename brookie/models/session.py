from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid7

from sqlalchemy import DateTime, Float, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from brookie.models.base import Base

if TYPE_CHECKING:
    from brookie.models.trip import Trip


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    location: Mapped[str] = mapped_column(String)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(String)

    trips: Mapped[list["Trip"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
