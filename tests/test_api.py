def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to MealFlow API"


def test_restaurants_endpoint(client):
    response = client.get("/restaurants/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_menu_endpoint(client):
    response = client.get("/menu/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
