from flask import Response


def test_index(client):
    # Mock
    path: str = '/'

    # Test
    response: Response = client.get(path)

    # Assert
    assert response is not None
    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.data.startswith(b'<!DOCTYPE HTML>')
    assert response.data.endswith(b'</html>')


def test_favicon(client):
    # Mock
    path: str = '/favicon.ico'

    # Test
    response: Response = client.get(path)

    # Assert
    assert response is not None
    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.data == b''


def test_robots(client):
    # Mock
    path: str = '/robots.txt'

    # Test
    response: Response = client.get(path)

    # Assert
    assert response is not None
    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.data == b''
