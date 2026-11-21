
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Cart, CartItem, MenuItem, Order, OrderItem, User
from app.schemas import OrderResponse
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# Place an order using the logged-in user's cart
@router.post(
    "/checkout",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def checkout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = (
        db.query(Cart)
        .options(
            joinedload(Cart.items).joinedload(CartItem.menu_item)
        )
        .filter(Cart.user_id == current_user.id)
        .first()
    )

    if cart is None or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your cart is empty"
        )

    total = Decimal("0.00")

    # Check availability and calculate the total
    for cart_item in cart.items:
        if not cart_item.menu_item.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{cart_item.menu_item.name} is unavailable"
            )

        total += cart_item.menu_item.price * cart_item.quantity

    try:
        # Create the main order
        new_order = Order(
            user_id=current_user.id,
            total_amount=total,
            status="placed"
        )

        db.add(new_order)
        db.flush()

        # Save each item with its purchase-time price
        for cart_item in cart.items:
            db.add(
                OrderItem(
                    order_id=new_order.id,
                    menu_item_id=cart_item.menu_item_id,
                    quantity=cart_item.quantity,
                    price=cart_item.menu_item.price
                )
            )

        # Clear the cart after preparing the order
        for cart_item in list(cart.items):
            db.delete(cart_item)

        db.commit()

    except Exception:
        db.rollback()
        raise

    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.id == new_order.id)
        .first()
    )


# Get all orders belonging to the logged-in user
@router.get("/", response_model=list[OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )


# Get one order belonging to the logged-in user
@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
        .first()
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return order
