from uuid import uuid4

from fastapi.testclient import TestClient


def test_create_trip_without_sessions(client: TestClient) -> None:
    response = client.post(
        "/trips",
        json={
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Trailhead",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["location"] == "Trailhead"
    assert body["sessions"] == []
    assert body["latitude"] is None
    assert body["notes"] is None


def test_create_trip_with_latitude_longitude_notes(client: TestClient) -> None:
    response = client.post(
        "/trips",
        json={
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Trailhead",
            "latitude": 45.5,
            "longitude": -73.6,
            "notes": "Sunny day",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["latitude"] == 45.5
    assert body["longitude"] == -73.6
    assert body["notes"] == "Sunny day"


def test_create_trip_rejects_partial_coordinates(client: TestClient) -> None:
    response = client.post(
        "/trips",
        json={
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Trailhead",
            "latitude": 45.5,
        },
    )
    assert response.status_code == 422


def test_list_trips(client: TestClient) -> None:
    client.post(
        "/trips",
        json={
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Trailhead",
        },
    )
    response = client.get("/trips")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_trip_not_found(client: TestClient) -> None:
    response = client.get(f"/trips/{uuid4()}")
    assert response.status_code == 404


def test_update_trip(client: TestClient) -> None:
    created = client.post(
        "/trips",
        json={
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Trailhead",
        },
    ).json()

    response = client.patch(f"/trips/{created['id']}", json={"location": "Summit"})
    assert response.status_code == 200
    assert response.json()["location"] == "Summit"
    assert response.json()["start_time"] == created["start_time"]


def test_update_trip_rejects_partial_coordinates(client: TestClient) -> None:
    created = client.post(
        "/trips",
        json={
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Trailhead",
        },
    ).json()

    response = client.patch(f"/trips/{created['id']}", json={"longitude": -73.6})
    assert response.status_code == 422


def test_delete_trip_cascades_sessions(client: TestClient) -> None:
    created = client.post(
        "/trips",
        json={
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T10:00:00+00:00",
            "location": "Trailhead",
        },
    ).json()
    session = client.post(
        "/sessions",
        json={
            "trip_id": created["id"],
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Leg 1",
        },
    ).json()

    delete_response = client.delete(f"/trips/{created['id']}")
    assert delete_response.status_code == 204

    assert client.get(f"/trips/{created['id']}").status_code == 404
    assert client.get(f"/sessions/{session['id']}").status_code == 404
