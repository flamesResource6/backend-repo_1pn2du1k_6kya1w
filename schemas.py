"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Events app schemas

class Event(BaseModel):
    """
    Events collection schema
    Collection name: "event"
    """
    title: str = Field(..., description="Event title")
    date: str = Field(..., description="ISO date string or human-readable date")
    venue: str = Field(..., description="Event venue")
    description: str = Field(..., description="Short description")
    image: str = Field(..., description="Hero image URL")
    price: float = Field(..., ge=0, description="Ticket price")
    tickets_available: int = Field(..., ge=0, description="Number of tickets available")

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    event_id: str = Field(..., description="ID of the event")
    name: str = Field(..., description="Buyer name")
    email: str = Field(..., description="Buyer email")
    quantity: int = Field(..., ge=1, description="Number of tickets")
    total_amount: float = Field(..., ge=0, description="Total price paid")
    status: str = Field("pending", description="Order status: pending, confirmed, cancelled")

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
