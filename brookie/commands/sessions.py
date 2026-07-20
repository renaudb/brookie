from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from brookie.commands.utils import check_coordinates
from brookie.models.session import Session
from brookie.models.trip import Trip


class TripNotFoundError(Exception):
    def __init__(self, trip_id: UUID) -> None:
        self.trip_id = trip_id
        super().__init__(f"Trip {trip_id} not found")


def create_session(
    db: DbSession,
    *,
    trip_id: UUID,
    start_time: datetime,
    end_time: datetime,
    location: str,
    latitude: float | None = None,
    longitude: float | None = None,
    notes: str | None = None,
) -> Session:
    trip = db.get(Trip, trip_id)
    if trip is None:
        raise TripNotFoundError(trip_id)
    check_coordinates(latitude, longitude)

    session = Session(
        trip_id=trip_id,
        start_time=start_time,
        end_time=end_time,
        location=location,
        latitude=latitude,
        longitude=longitude,
        notes=notes,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: DbSession, session_id: UUID) -> Session | None:
    return db.get(Session, session_id)


def list_sessions(db: DbSession, *, trip_id: UUID | None = None) -> Sequence[Session]:
    stmt = select(Session)
    if trip_id is not None:
        stmt = stmt.where(Session.trip_id == trip_id)
    return db.execute(stmt).scalars().all()


def update_session(
    db: DbSession,
    session_id: UUID,
    *,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    location: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    notes: str | None = None,
) -> Session | None:
    session = db.get(Session, session_id)
    if session is None:
        return None

    final_latitude = latitude if latitude is not None else session.latitude
    final_longitude = longitude if longitude is not None else session.longitude
    check_coordinates(final_latitude, final_longitude)

    if start_time is not None:
        session.start_time = start_time
    if end_time is not None:
        session.end_time = end_time
    if location is not None:
        session.location = location
    if latitude is not None:
        session.latitude = latitude
    if longitude is not None:
        session.longitude = longitude
    if notes is not None:
        session.notes = notes

    db.commit()
    db.refresh(session)
    return session


def delete_session(db: DbSession, session_id: UUID) -> bool:
    session = db.get(Session, session_id)
    if session is None:
        return False

    db.delete(session)
    db.commit()
    return True
