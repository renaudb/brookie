from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from brookie.commands.utils import check_coordinates
from brookie.models.trip import Trip


def create_trip(
    db: DbSession,
    *,
    start_time: datetime,
    end_time: datetime,
    location: str,
    latitude: float | None = None,
    longitude: float | None = None,
    notes: str | None = None,
) -> Trip:
    check_coordinates(latitude, longitude)

    trip = Trip(
        start_time=start_time,
        end_time=end_time,
        location=location,
        latitude=latitude,
        longitude=longitude,
        notes=notes,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


def get_trip(db: DbSession, trip_id: UUID) -> Trip | None:
    return db.get(Trip, trip_id)


def list_trips(db: DbSession) -> Sequence[Trip]:
    return db.execute(select(Trip)).scalars().all()


def update_trip(
    db: DbSession,
    trip_id: UUID,
    *,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    location: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    notes: str | None = None,
) -> Trip | None:
    trip = db.get(Trip, trip_id)
    if trip is None:
        return None

    final_latitude = latitude if latitude is not None else trip.latitude
    final_longitude = longitude if longitude is not None else trip.longitude
    check_coordinates(final_latitude, final_longitude)

    if start_time is not None:
        trip.start_time = start_time
    if end_time is not None:
        trip.end_time = end_time
    if location is not None:
        trip.location = location
    if latitude is not None:
        trip.latitude = latitude
    if longitude is not None:
        trip.longitude = longitude
    if notes is not None:
        trip.notes = notes

    db.commit()
    db.refresh(trip)
    return trip


def delete_trip(db: DbSession, trip_id: UUID) -> bool:
    trip = db.get(Trip, trip_id)
    if trip is None:
        return False

    db.delete(trip)
    db.commit()
    return True
