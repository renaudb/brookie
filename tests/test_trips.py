from fastapi.testclient import TestClient


def _create_session(client: TestClient) -> int:
    response = client.post(
        "/sessions",
        json={
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Trailhead",
        },
    )
    session_id: int = response.json()["id"]
    return session_id


def test_create_trip_for_existing_session(client: TestClient) -> None:
    session_id = _create_session(client)

    response = client.post(
        "/trips",
        json={
            "session_id": session_id,
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Leg 1",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["session_id"] == session_id
    assert body["location"] == "Leg 1"


def test_create_trip_missing_session_returns_404(client: TestClient) -> None:
    response = client.post(
        "/trips",
        json={
            "session_id": 999,
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Leg 1",
        },
    )
    assert response.status_code == 404


def test_list_trips_filtered_by_session(client: TestClient) -> None:
    session_id = _create_session(client)
    other_session_id = _create_session(client)

    client.post(
        "/trips",
        json={
            "session_id": session_id,
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Leg 1",
        },
    )
    client.post(
        "/trips",
        json={
            "session_id": other_session_id,
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Other leg",
        },
    )

    response = client.get("/trips", params={"session_id": session_id})
    assert response.status_code == 200
    trips = response.json()
    assert len(trips) == 1
    assert trips[0]["location"] == "Leg 1"

    assert len(client.get("/trips").json()) == 2


def test_get_trip_not_found(client: TestClient) -> None:
    assert client.get("/trips/999").status_code == 404


def test_update_trip(client: TestClient) -> None:
    session_id = _create_session(client)
    trip = client.post(
        "/trips",
        json={
            "session_id": session_id,
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Leg 1",
        },
    ).json()

    response = client.patch(f"/trips/{trip['id']}", json={"location": "Updated leg"})
    assert response.status_code == 200
    assert response.json()["location"] == "Updated leg"


def test_delete_trip(client: TestClient) -> None:
    session_id = _create_session(client)
    trip = client.post(
        "/trips",
        json={
            "session_id": session_id,
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Leg 1",
        },
    ).json()

    assert client.delete(f"/trips/{trip['id']}").status_code == 204
    assert client.get(f"/trips/{trip['id']}").status_code == 404


def test_create_session_trip_nested_route(client: TestClient) -> None:
    session_id = _create_session(client)

    response = client.post(
        f"/sessions/{session_id}/trips",
        json={
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Leg 1",
        },
    )
    assert response.status_code == 201
    assert response.json()["session_id"] == session_id

    assert client.get(f"/sessions/{session_id}/trips").json()[0]["location"] == "Leg 1"


def test_create_session_trip_nested_route_missing_session(client: TestClient) -> None:
    response = client.post(
        "/sessions/999/trips",
        json={
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Leg 1",
        },
    )
    assert response.status_code == 404
