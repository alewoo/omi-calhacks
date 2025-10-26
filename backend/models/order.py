"""Pydantic models for food ordering"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class OrderIntent(BaseModel):
    """Parsed food order intent from voice"""
    food_item: str
    restaurant: Optional[str] = None
    cuisine: Optional[str] = None
    dietary_restrictions: List[str] = []
    quick_order: bool = False  # "order my usual"
    delivery_instructions: Optional[str] = None
    confidence: float = 0.0  # 0-1 confidence score


class FavoriteOrder(BaseModel):
    """A saved favorite order"""
    restaurant: str
    food_item: str
    last_ordered: datetime
    order_count: int = 1


class UserProfile(BaseModel):
    """User profile stored in Redis"""
    uid: str
    delivery_address: Optional[str] = None
    phone: Optional[str] = None
    favorite_restaurants: List[str] = []
    favorite_orders: List[FavoriteOrder] = []
    dietary_preferences: List[str] = []  # ["vegetarian", "gluten-free", etc]
    last_order: Optional[OrderIntent] = None


class OrderResult(BaseModel):
    """Result of placing an order"""
    status: str  # "success", "pending", "failed"
    order_id: Optional[str] = None
    restaurant: str
    items: List[str]
    total: Optional[float] = None
    eta: Optional[str] = None
    tracking_url: Optional[str] = None
    deep_link: Optional[str] = None  # For fallback ordering
