class IncompleteCoordinatesError(Exception):
    def __init__(self) -> None:
        super().__init__("latitude and longitude must both be set or both be null")


def check_coordinates(latitude: float | None, longitude: float | None) -> None:
    if (latitude is None) != (longitude is None):
        raise IncompleteCoordinatesError()
