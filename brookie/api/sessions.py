from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session as DbSession

from brookie.api.trips import TripCreateNested, TripRead
from brookie.commands import sessions as session_commands
from brookie.commands import trips as trip_commands
from brookie.commands.trips import SessionNotFoundError, TripInput
from brookie.db import get_db

router = APIRouter(prefix="/sessions", tags=["sessions"])


class SessionBase(BaseModel):
    start_time: datetime
    end_time: datetime
    location: str


class SessionCreate(SessionBase):
    trips: list[TripCreateNested] = []


class SessionUpdate(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None
    location: str | None = None


class SessionRead(SessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trips: list[TripRead] = []


@router.post("", status_code=201)
def create_session(
    payload: SessionCreate, db: DbSession = Depends(get_db)
) -> SessionRead:
    trip_inputs = [
        TripInput(start_time=t.start_time, end_time=t.end_time, location=t.location)
        for t in payload.trips
    ]
    session = session_commands.create_session(
        db,
        start_time=payload.start_time,
        end_time=payload.end_time,
        location=payload.location,
        trips=trip_inputs,
    )
    return SessionRead.model_validate(session)


@router.get("")
def list_sessions(db: DbSession = Depends(get_db)) -> list[SessionRead]:
    sessions = session_commands.list_sessions(db)
    return [SessionRead.model_validate(session) for session in sessions]


@router.get("/{session_id}")
def get_session(session_id: int, db: DbSession = Depends(get_db)) -> SessionRead:
    session = session_commands.get_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionRead.model_validate(session)


@router.patch("/{session_id}")
def update_session(
    session_id: int, payload: SessionUpdate, db: DbSession = Depends(get_db)
) -> SessionRead:
    session = session_commands.update_session(
        db,
        session_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        location=payload.location,
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionRead.model_validate(session)


@router.delete("/{session_id}", status_code=204)
def delete_session(session_id: int, db: DbSession = Depends(get_db)) -> None:
    deleted = session_commands.delete_session(db, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")


@router.post("/{session_id}/trips", status_code=201)
def create_session_trip(
    session_id: int, payload: TripCreateNested, db: DbSession = Depends(get_db)
) -> TripRead:
    try:
        trip = trip_commands.create_trip(
            db,
            session_id=session_id,
            start_time=payload.start_time,
            end_time=payload.end_time,
            location=payload.location,
        )
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return TripRead.model_validate(trip)


@router.get("/{session_id}/trips")
def list_session_trips(
    session_id: int, db: DbSession = Depends(get_db)
) -> list[TripRead]:
    if session_commands.get_session(db, session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    trips = trip_commands.list_trips(db, session_id=session_id)
    return [TripRead.model_validate(trip) for trip in trips]
