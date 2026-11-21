from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MenuItem, Restaurant
from app.schemas import MenuItemCreate, MenuItemResponse
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/menu",
    tags=["Menu"]
)


# Add a food item to a restaurant menu (login required)
@router.post(
    "/",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED
)
def create_menu_item(
    item_data: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Check whether the restaurant exists and is active
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == item_data.restaurant_id,
        Restaurant.is_active == True
    ).first()

    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )

    new_item = MenuItem(
        name=item_data.name,
        description=item_data.description,
        price=item_data.price,
        restaurant_id=item_data.restaurant_id
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


# Get available menu items, optionally for one restaurant
@router.get("/", response_model=list[MenuItemResponse])
def get_menu_items(
    restaurant_id: int | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(MenuItem).filter(
        MenuItem.is_available == True
    )

    if restaurant_id is not None:
        query = query.filter(
            MenuItem.restaurant_id == restaurant_id
        )

    return query.offset(skip).limit(limit).all()


# Get one menu item using its ID
@router.get("/{item_id}", response_model=MenuItemResponse)
def get_menu_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    item = db.query(MenuItem).filter(
        MenuItem.id == item_id,
        MenuItem.is_available == True
    ).first()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )

    return item