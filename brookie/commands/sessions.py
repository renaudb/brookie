from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from brookie.commands.trips import TripInput
from brookie.models.session import Session
from brookie.models.trip import Trip


def create_session(
    db: DbSession,
    *,
    start_time: datetime,
    end_time: datetime,
    location: str,
    latitude: float | None = None,
    longitude: float | None = None,
    notes: str | None = None,
    trips: list[TripInput] | None = None,
) -> Session:
    session = Session(
        start_time=start_time,
        end_time=end_time,
        location=location,
        latitude=latitude,
        longitude=longitude,
        notes=notes,
    )
    if trips:
        session.trips = [
            Trip(
                start_time=t.start_time,
                end_time=t.end_time,
                location=t.location,
                latitude=t.latitude,
                longitude=t.longitude,
                notes=t.notes,
            )
            for t in trips
        ]

    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: DbSession, session_id: UUID) -> Session | None:
    return db.get(Session, session_id)


def list_sessions(db: DbSession) -> Sequence[Session]:
    return db.execute(select(Session)).scalars().all()


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
