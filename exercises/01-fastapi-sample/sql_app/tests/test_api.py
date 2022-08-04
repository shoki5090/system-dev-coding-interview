
from secrets import token_hex
"""
[O] Read Users
[O] Create User
[O] Read User
[O] Create Item for User
[] Read Items
[O] Read User Items
[] Delete User
"""
def _check_wrong_api(response):
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] =="API Token not found or not active"

def test_create_user(test_db, client, create_user):
    """
    Create User
    Read User
    """
    data = create_user
    assert data["email"] == "deadpool@example.com"
    assert "id" in data
    assert "api_token" in data

    user_id = data["id"]
    api_token = data["api_token"]
    
    response = client.get(f"/users/{user_id}", headers={"x-api-token": api_token})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "deadpool@example.com"
    assert data["id"] == user_id

def test_add_user_item(test_db, client, create_user, create_second_user, dummy_items):
    """
    Create User for item
    """
    data = create_user
    user_id = data["id"]
    api_token = data["api_token"]

    # add single item
    response = client.post(
        f"/users/{user_id}/items/",
        json=dummy_items[0],
        headers={"x-api-token": api_token}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == dummy_items[0]["title"]
    assert data["description"] == dummy_items[0]["description"]
    assert data["owner_id"] == user_id

def test_wrong_api_token(test_db, client, create_user, dummy_items):
    """
    Send wrong API token to each endpoint
    """
    data = create_user
    user_id = data["id"]

    # create user item
    response = client.post(
        f"/users/{user_id}/items/",
        json=dummy_items[0],
        headers={"x-api-token": token_hex(16)}
    )
    _check_wrong_api(response)

    #get user from user id
    response = client.get(
        f"/users/{user_id}/",
        headers={"x-api-token": token_hex(16)}
    )
    _check_wrong_api(response)

    # Read items
    response = client.get(
        f"/items/",
        headers={"x-api-token": token_hex(16)}
    )
    _check_wrong_api(response)

    # Get My Item
    response = client.get(
        f"/me/items/",
        headers={"x-api-token": token_hex(16)}
    )
    _check_wrong_api(response)

    # Delete User
    response = client.post(
        f"/delete_user/{user_id}",
        headers={"x-api-token": token_hex(16)}
    )
    _check_wrong_api(response)



def test_get_user_item(test_db, client, create_user, create_second_user, dummy_items):
    """
    Get User Items
    """
    data = create_user
    data2 = create_second_user

    user_id = data["id"]
    api_token = data["api_token"]

    user_id2 = data2["id"]
    api_token2 = data2["api_token"]
    # add multiple items
    client.post(
        f"/users/{user_id}/items/",
        json=dummy_items[0],
        headers={"x-api-token": api_token}
    )
    client.post(
        f"/users/{user_id}/items/",
        json=dummy_items[1],
        headers={"x-api-token": api_token}
    )

    client.post(
        f"/users/{user_id2}/items/",
        json=dummy_items[0],
        headers={"x-api-token": api_token2}
    )

    response = client.get(
        f"/me/items/",
        headers={"x-api-token": api_token}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    
    assert data[0]["title"] == dummy_items[0]["title"]
    assert data[0]["description"] == dummy_items[0]["description"]
    assert data[0]["owner_id"] == user_id
    assert data[1]["title"] == dummy_items[1]["title"]
    assert data[1]["description"] == dummy_items[1]["description"]
    assert data[1]["owner_id"] == user_id
    assert len(data) == 2
    
def test_get_users(test_db, client, create_user):
    """
    Read Users
    """
    data1 = create_user
    response = client.post(
        "/users/",
        json={"email": "ironman@example.com", "password": "shoyuRamen"},
    )
    assert response.status_code == 200, response.text
    data2 = response.json()


    response = client.get(
        "/users/",
        headers={"x-api-token": data1["api_token"]}
    )
    assert response.status_code == 200, response.text
    data = response.json()

    assert data[0]["email"] == "deadpool@example.com"
    assert data[0]["id"] == data1["id"]
    assert data[1]["email"] == "ironman@example.com"
    assert data[1]["id"] == data2["id"]









    