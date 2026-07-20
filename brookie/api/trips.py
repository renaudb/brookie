from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session as DbSession

from brookie.api.sessions import SessionRead
from brookie.commands import trips as trip_commands
from brookie.commands.utils import IncompleteCoordinatesError
from brookie.db import get_db

router = APIRouter(prefix="/trips", tags=["trips"])


class TripBase(BaseModel):
    start_time: datetime
    end_time: datetime
    location: str
    latitude: float | None = None
    longitude: float | None = None
    notes: str | None = None


class TripUpdate(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    notes: str | None = None


class TripRead(TripBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sessions: list[SessionRead] = []


@router.post("", status_code=201)
def create_trip(payload: TripBase, db: DbSession = Depends(get_db)) -> TripRead:
    try:
        trip = trip_commands.create_trip(
            db,
            start_time=payload.start_time,
            end_time=payload.end_time,
            location=payload.location,
            latitude=payload.latitude,
            longitude=payload.longitude,
            notes=payload.notes,
        )
    except IncompleteCoordinatesError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return TripRead.model_validate(trip)


@router.get("")
def list_trips(db: DbSession = Depends(get_db)) -> list[TripRead]:
    trips = trip_commands.list_trips(db)
    return [TripRead.model_validate(trip) for trip in trips]


@router.get("/{trip_id}")
def get_trip(trip_id: UUID, db: DbSession = Depends(get_db)) -> TripRead:
    trip = trip_commands.get_trip(db, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return TripRead.model_validate(trip)


@router.patch("/{trip_id}")
def update_trip(
    trip_id: UUID, payload: TripUpdate, db: DbSession = Depends(get_db)
) -> TripRead:
    try:
        trip = trip_commands.update_trip(
            db,
            trip_id,
            start_time=payload.start_time,
            end_time=payload.end_time,
            location=payload.location,
            latitude=payload.latitude,
            longitude=payload.longitude,
            notes=payload.notes,
        )
    except IncompleteCoordinatesError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return TripRead.model_validate(trip)


@router.delete("/{trip_id}", status_code=204)
def delete_trip(trip_id: UUID, db: DbSession = Depends(get_db)) -> None:
    deleted = trip_commands.delete_trip(db, trip_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Trip not found")
