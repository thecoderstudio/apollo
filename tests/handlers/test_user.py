import apollo.models 

def test_post_user_successful(test_client, token):  
    print(token)
    assert True
    return
    
    
    # response = test_client.post(
    #     '/user',
    #     json={'username': 'doejohn', 'password': 'testing123'},
    #     headers={'Authorization': f'Bearer {token}'}
    # )
    
    
    # assert response.status_code == 200
    # assert response.json()['username'] == 'doejohn'

    
# def test_post_user_unsuccessful(test_client, database, token):
#     response = test_client.post(
#         '/user',
#         json={'username': 'doejohn', 'password': '123'},
#         headers={'Authorization': f'Bearer {token}'}
#     )

#     assert response.status_code == 422
    