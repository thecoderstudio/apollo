def test_validation_error_schema(test_client):
    response = test_client.post(
        '/user',
        json={'username': 'username', 'password': ''},
    )

    assert response.status_code == 400
    error_body = response.json()['password']
    assert error_body['msg'] == 'ensure this value has at least 8 characters'
    assert error_body['type'] == 'value_error.any_str.min_length'
    assert error_body['errors'] == {'limit_value': 8}
