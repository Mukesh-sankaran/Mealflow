from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Cart, CartItem, MenuItem, User
from app.schemas import CartItemCreate, CartItemUpdate, CartResponse
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


# Find the user's cart or create one if it does not exist
def get_or_create_cart(db: Session, user_id: int):
    cart = db.query(Cart).filter(
        Cart.user_id == user_id
    ).first()

    if cart is None:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


# Prepare cart data and calculate item and cart totals
def build_cart_response(cart: Cart):
    items = []
    total = Decimal("0.00")

    for cart_item in cart.items:
        subtotal = (
            cart_item.menu_item.price * cart_item.quantity
        )

        total += subtotal

        items.append({
            "id": cart_item.id,
            "menu_item_id": cart_item.menu_item_id,
            "quantity": cart_item.quantity,
            "menu_item": cart_item.menu_item,
            "subtotal": subtotal
        })

    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "items": items,
        "total_amount": total
    }


# View the logged-in user's cart
@router.get("/", response_model=CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = get_or_create_cart(db, current_user.id)

    cart = (
        db.query(Cart)
        .options(
            joinedload(Cart.items).joinedload(CartItem.menu_item)
        )
        .filter(Cart.id == cart.id)
        .first()
    )

    return build_cart_response(cart)


# Add a food item to the cart
@router.post("/items", response_model=CartResponse)
def add_to_cart(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = get_or_create_cart(db, current_user.id)

    menu_item = db.query(MenuItem).filter(
        MenuItem.id == item_data.menu_item_id,
        MenuItem.is_available == True
    ).first()

    if menu_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found or unavailable"
        )

    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.menu_item_id == menu_item.id
    ).first()

    if cart_item:
        cart_item.quantity += item_data.quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            menu_item_id=menu_item.id,
            quantity=item_data.quantity
        )
        db.add(cart_item)

    db.commit()

    updated_cart = (
        db.query(Cart)
        .options(
            joinedload(Cart.items).joinedload(CartItem.menu_item)
        )
        .filter(Cart.id == cart.id)
        .first()
    )

    return build_cart_response(updated_cart)


# Change the quantity of an item in the cart
@router.patch("/items/{cart_item_id}", response_model=CartResponse)
def update_cart_item(
    cart_item_id: int,
    item_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = get_or_create_cart(db, current_user.id)

    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.cart_id == cart.id
    ).first()

    if cart_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    cart_item.quantity = item_data.quantity
    db.commit()

    updated_cart = (
        db.query(Cart)
        .options(
            joinedload(Cart.items).joinedload(CartItem.menu_item)
        )
        .filter(Cart.id == cart.id)
        .first()
    )

    return build_cart_response(updated_cart)


# Remove an item from the cart
@router.delete("/items/{cart_item_id}", response_model=CartResponse)
def remove_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = get_or_create_cart(db, current_user.id)

    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.cart_id == cart.id
    ).first()

    if cart_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    db.delete(cart_item)
    db.commit()

    updated_cart = (
        db.query(Cart)
        .options(
            joinedload(Cart.items).joinedload(CartItem.menu_item)
        )
        .filter(Cart.id == cart.id)
        .first()
    )

    return build_cart_response(updated_cart)