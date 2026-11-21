from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Restaurant
from app.schemas import RestaurantCreate, RestaurantResponse
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurants"]
)


# Create a restaurant (login required)
@router.post(
    "/",
    response_model=RestaurantResponse,
    status_code=status.HTTP_201_CREATED
)
def create_restaurant(
    restaurant_data: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_restaurant = Restaurant(
        name=restaurant_data.name,
        address=restaurant_data.address
    )

    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)

    return new_restaurant


# Get all active restaurants
@router.get("/", response_model=list[RestaurantResponse])
def get_restaurants(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    return (
        db.query(Restaurant)
        .filter(Restaurant.is_active == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


# Get one restaurant using its ID
@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db)
):
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id,
        Restaurant.is_active == True
    ).first()

    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )

    return restaurant