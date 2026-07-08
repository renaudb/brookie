from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid7

from sqlalchemy import DateTime, Float, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from brookie.models.base import Base

if TYPE_CHECKING:
    from brookie.models.session import Session


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    session_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("sessions.id", ondelete="CASCADE")
    )
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    location: Mapped[str] = mapped_column(String)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(String)

    session: Mapped["Session"] = relationship(back_populates="trips")
