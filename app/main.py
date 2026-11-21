from fastapi import FastAPI

from app.routers import users, restaurants, menu, cart, orders


app = FastAPI(
    title="MealFlow API",
    description="Food ordering backend built with FastAPI and PostgreSQL",
    version="1.0.0"
)


# Connect all API routers
app.include_router(users.router)
app.include_router(restaurants.router)
app.include_router(menu.router)
app.include_router(cart.router)
app.include_router(orders.router)


@app.get("/")
def home():
    return {"message": "Welcome to MealFlow API"}