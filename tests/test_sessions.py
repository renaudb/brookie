from uuid import uuid4

from fastapi.testclient import TestClient

MISSING_UUID = str(uuid4())


def _create_trip(client: TestClient) -> str:
    response = client.post(
        "/trips",
        json={
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Trailhead",
        },
    )
    trip_id: str = response.json()["id"]
    return trip_id


def test_create_session_for_existing_trip(client: TestClient) -> None:
    trip_id = _create_trip(client)

    response = client.post(
        "/sessions",
        json={
            "trip_id": trip_id,
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Leg 1",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["trip_id"] == trip_id
    assert body["location"] == "Leg 1"


def test_create_session_missing_trip_returns_404(client: TestClient) -> None:
    response = client.post(
        "/sessions",
        json={
            "trip_id": MISSING_UUID,
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Leg 1",
        },
    )
    assert response.status_code == 404


def test_list_sessions_filtered_by_trip(client: TestClient) -> None:
    trip_id = _create_trip(client)
    other_trip_id = _create_trip(client)

    client.post(
        "/sessions",
        json={
            "trip_id": trip_id,
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Leg 1",
        },
    )
    client.post(
        "/sessions",
        json={
            "trip_id": other_trip_id,
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Other leg",
        },
    )

    response = client.get("/sessions", params={"trip_id": trip_id})
    assert response.status_code == 200
    sessions = response.json()
    assert len(sessions) == 1
    assert sessions[0]["location"] == "Leg 1"

    assert len(client.get("/sessions").json()) == 2


def test_get_session_not_found(client: TestClient) -> None:
    assert client.get(f"/sessions/{MISSING_UUID}").status_code == 404


def test_update_session(client: TestClient) -> None:
    trip_id = _create_trip(client)
    session = client.post(
        "/sessions",
        json={
            "trip_id": trip_id,
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Leg 1",
        },
    ).json()

    response = client.patch(
        f"/sessions/{session['id']}", json={"location": "Updated leg"}
    )
    assert response.status_code == 200
    assert response.json()["location"] == "Updated leg"


def test_create_session_rejects_partial_coordinates(client: TestClient) -> None:
    trip_id = _create_trip(client)

    response = client.post(
        "/sessions",
        json={
            "trip_id": trip_id,
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Leg 1",
            "longitude": -73.6,
        },
    )
    assert response.status_code == 422


def test_update_session_rejects_partial_coordinates(client: TestClient) -> None:
    trip_id = _create_trip(client)
    session = client.post(
        "/sessions",
        json={
            "trip_id": trip_id,
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Leg 1",
        },
    ).json()

    response = client.patch(f"/sessions/{session['id']}", json={"latitude": 45.5})
    assert response.status_code == 422


def test_update_session_latitude_longitude_notes(client: TestClient) -> None:
    trip_id = _create_trip(client)
    session = client.post(
        "/sessions",
        json={
            "trip_id": trip_id,
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Leg 1",
        },
    ).json()
    assert session["latitude"] is None
    assert session["longitude"] is None
    assert session["notes"] is None

    response = client.patch(
        f"/sessions/{session['id']}",
        json={"latitude": 45.5, "longitude": -73.6, "notes": "Rained a lot"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["latitude"] == 45.5
    assert body["longitude"] == -73.6
    assert body["notes"] == "Rained a lot"


def test_delete_session(client: TestClient) -> None:
    trip_id = _create_trip(client)
    session = client.post(
        "/sessions",
        json={
            "trip_id": trip_id,
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Leg 1",
        },
    ).json()

    assert client.delete(f"/sessions/{session['id']}").status_code == 204
    assert client.get(f"/sessions/{session['id']}").status_code == 404
