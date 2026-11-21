from uuid import uuid4


def test_complete_mealflow_workflow(client):
    email = f"test_{uuid4().hex[:8]}@example.com"
    password = "MealFlowTest@123"

    # Register
    response = client.post("/users/register", json={
        "name": "Test User",
        "email": email,
        "password": password
    })
    assert response.status_code == 201

    # Login and obtain JWT
    response = client.post("/users/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Create restaurant
    response = client.post("/restaurants/", headers=headers, json={
        "name": "Test Restaurant",
        "address": "Chennai"
    })
    assert response.status_code == 201
    restaurant_id = response.json()["id"]

    # Create menu item
    response = client.post("/menu/", headers=headers, json={
        "name": "Test Burger",
        "description": "Test item",
        "price": "150.00",
        "restaurant_id": restaurant_id
    })
    assert response.status_code == 201
    item_id = response.json()["id"]

    # Add item to cart
    response = client.post("/cart/items", headers=headers, json={
        "menu_item_id": item_id,
        "quantity": 2
    })
    assert response.status_code == 200

    # Verify cart
    response = client.get("/cart/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1

    # Checkout
    response = client.post("/orders/checkout", headers=headers)
    assert response.status_code == 201
    order_id = response.json()["id"]
    assert response.json()["status"] == "placed"

    # Verify order history
    response = client.get("/orders/", headers=headers)
    assert response.status_code == 200
    assert any(order["id"] == order_id for order in response.json())

    # Cancel order
    response = client.patch(
        f"/orders/{order_id}/cancel",
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_protected_cart_requires_login(client):
    response = client.get("/cart/")
    assert response.status_code == 401
