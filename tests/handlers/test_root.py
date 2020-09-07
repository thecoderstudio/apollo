def test_correct_version(test_client):
    expected_version = '1.0'

    response = test_client.get("/")

    assert response.status_code == 200
    assert response.json() == {'version': expected_version}
