
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Numeric,
    DateTime,
    func
)
from sqlalchemy.orm import relationship

from app.database import Base


# Stores information about registered users
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Connect this user to their cart and orders
    cart = relationship("Cart", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="user")


# Stores information about restaurants
class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    address = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    # Connect a restaurant to all its menu items
    menu_items = relationship("MenuItem", back_populates="restaurant")


# Stores food items offered by restaurants
class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(String(500))
    price = Column(Numeric(10, 2), nullable=False)
    is_available = Column(Boolean, default=True)

    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))

    # Find which restaurant this food item belongs to
    restaurant = relationship("Restaurant", back_populates="menu_items")


# Stores one shopping cart for each user
class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    # Connect the cart to its owner and its items
    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart")


# Stores individual food items added to a cart
class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer, nullable=False, default=1)

    # Connect this item to its cart and food item
    cart = relationship("Cart", back_populates="items")
    menu_item = relationship("MenuItem")


# Stores orders placed by users
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default="placed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Connect the order to its user and ordered items
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


# Stores individual food items inside an order
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    # Connect this item to its order and food item
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")
