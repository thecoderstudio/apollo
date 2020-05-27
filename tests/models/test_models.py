from apollo.models import get_connection_url


def test_get_connection_url():
    connection_url = get_connection_url({
        'SQLAlchemy': {
            'driver': 'postgresql',
            'user': 'test',
            'password': 'test',
            'host': 'localhost',
            'database': 'test'
        }
    })

    assert connection_url == "postgresql://test:test@localhost/test"
