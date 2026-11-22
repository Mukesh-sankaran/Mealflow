import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users, restaurants, menu, cart, orders


app = FastAPI(
    title="MealFlow API",
    description="Food ordering backend built with FastAPI and PostgreSQL",
    version="1.0.0"
)


# Allow the deployed frontend and local development frontend
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:5174"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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