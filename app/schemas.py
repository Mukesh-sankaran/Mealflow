
from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from datetime import datetime


# Allow Pydantic to read data directly from SQLAlchemy objects
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------------- USER SCHEMAS ----------------

# Data required when someone creates an account
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str
    password: str = Field(min_length=8)


# Data required when someone logs in
class UserLogin(BaseModel):
    email: str
    password: str


# Data returned after registration or login
class UserResponse(BaseSchema):
    id: int
    name: str
    email: str


# ---------------- RESTAURANT SCHEMAS ----------------

# Data required to create a restaurant
class RestaurantCreate(BaseModel):
    name: str
    address: str


# Data returned when displaying a restaurant
class RestaurantResponse(BaseSchema):
    id: int
    name: str
    address: str
    is_active: bool


# ---------------- MENU SCHEMAS ----------------

# Data required to add food to a restaurant menu
class MenuItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: Decimal = Field(gt=0)
    restaurant_id: int


# Data returned when displaying a food item
class MenuItemResponse(BaseSchema):
    id: int
    name: str
    description: str | None
    price: Decimal
    is_available: bool
    restaurant_id: int


# ---------------- CART SCHEMAS ----------------

# Data required when adding food to a cart
class CartItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = Field(default=1, gt=0)


# ---------------- ORDER SCHEMAS ----------------

# Information about each food item inside an order
class OrderItemResponse(BaseSchema):
    id: int
    menu_item_id: int
    quantity: int
    price: Decimal
    menu_item: MenuItemResponse


# Information returned about an order
class OrderResponse(BaseSchema):
    id: int
    user_id: int
    total_amount: Decimal
    status: str
    created_at: datetime
    items: list[OrderItemResponse]



# Data returned after successful login
class Token(BaseModel):
    access_token: str
    token_type: str


# ---------------- CART RESPONSE SCHEMAS ----------------

# Data required when changing cart quantity
class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


# Information about one item displayed in the cart
class CartLineResponse(BaseSchema):
    id: int
    menu_item_id: int
    quantity: int
    menu_item: MenuItemResponse
    subtotal: Decimal


# Information returned when displaying a cart
class CartResponse(BaseModel):
    id: int
    user_id: int
    items: list[CartLineResponse]
    total_amount: Decimal
