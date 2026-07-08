from fastapi.testclient import TestClient


def test_create_session_without_trips(client: TestClient) -> None:
    response = client.post(
        "/sessions",
        json={
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Trailhead",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["location"] == "Trailhead"
    assert body["trips"] == []


def test_create_session_with_nested_trips(client: TestClient) -> None:
    response = client.post(
        "/sessions",
        json={
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T10:00:00+00:00",
            "location": "Trailhead",
            "trips": [
                {
                    "start_time": "2024-01-01T08:00:00+00:00",
                    "end_time": "2024-01-01T09:00:00+00:00",
                    "location": "Leg 1",
                },
                {
                    "start_time": "2024-01-01T09:00:00+00:00",
                    "end_time": "2024-01-01T10:00:00+00:00",
                    "location": "Leg 2",
                },
            ],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert len(body["trips"]) == 2
    assert {trip["location"] for trip in body["trips"]} == {"Leg 1", "Leg 2"}
    assert all(trip["session_id"] == body["id"] for trip in body["trips"])


def test_list_sessions(client: TestClient) -> None:
    client.post(
        "/sessions",
        json={
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Trailhead",
        },
    )
    response = client.get("/sessions")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_session_not_found(client: TestClient) -> None:
    response = client.get("/sessions/999")
    assert response.status_code == 404


def test_update_session(client: TestClient) -> None:
    created = client.post(
        "/sessions",
        json={
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T09:00:00+00:00",
            "location": "Trailhead",
        },
    ).json()

    response = client.patch(f"/sessions/{created['id']}", json={"location": "Summit"})
    assert response.status_code == 200
    assert response.json()["location"] == "Summit"
    assert response.json()["start_time"] == created["start_time"]


def test_delete_session_cascades_trips(client: TestClient) -> None:
    created = client.post(
        "/sessions",
        json={
            "start_time": "2024-01-01T08:00:00+00:00",
            "end_time": "2024-01-01T10:00:00+00:00",
            "location": "Trailhead",
            "trips": [
                {
                    "start_time": "2024-01-01T08:00:00+00:00",
                    "end_time": "2024-01-01T09:00:00+00:00",
                    "location": "Leg 1",
                }
            ],
        },
    ).json()
    trip_id = created["trips"][0]["id"]

    delete_response = client.delete(f"/sessions/{created['id']}")
    assert delete_response.status_code == 204

    assert client.get(f"/sessions/{created['id']}").status_code == 404
    assert client.get(f"/trips/{trip_id}").status_code == 404
