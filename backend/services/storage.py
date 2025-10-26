"""Redis storage service for user profiles and order history"""
import json
import os
from typing import Optional
import redis
from datetime import datetime
from models.order import UserProfile, OrderIntent, FavoriteOrder


class StorageService:
    """Handle all Redis storage operations"""

    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            print("✅ Connected to Redis")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            print("📝 Using in-memory fallback (data won't persist)")
            self.redis_client = None
            self.memory_store = {}  # Fallback to in-memory dict

    def get_user_profile(self, uid: str) -> UserProfile:
        """
        Get user profile from storage

        Args:
            uid: User ID from Omi

        Returns:
            UserProfile (creates new one if doesn't exist)
        """
        key = f"user_profile:{uid}"

        try:
            if self.redis_client:
                data = self.redis_client.get(key)
                if data:
                    return UserProfile(**json.loads(data))
            else:
                # Fallback to memory
                if key in self.memory_store:
                    return UserProfile(**self.memory_store[key])
        except Exception as e:
            print(f"Error getting user profile: {e}")

        # Return new profile if not found
        return UserProfile(uid=uid)

    def save_user_profile(self, profile: UserProfile) -> bool:
        """
        Save user profile to storage

        Args:
            profile: UserProfile to save

        Returns:
            True if successful
        """
        key = f"user_profile:{profile.uid}"

        try:
            data = profile.model_dump_json()

            if self.redis_client:
                self.redis_client.set(key, data)
            else:
                # Fallback to memory
                self.memory_store[key] = json.loads(data)

            return True

        except Exception as e:
            print(f"Error saving user profile: {e}")
            return False

    def save_last_order(self, uid: str, order: OrderIntent) -> bool:
        """
        Save user's last order for "order my usual" functionality

        Args:
            uid: User ID
            order: OrderIntent to save

        Returns:
            True if successful
        """
        # Get profile
        profile = self.get_user_profile(uid)

        # Update last order
        profile.last_order = order

        # Update favorites list
        if order.restaurant and order.food_item:
            # Check if this order already exists in favorites
            existing = next(
                (f for f in profile.favorite_orders
                 if f.restaurant == order.restaurant and f.food_item == order.food_item),
                None
            )

            if existing:
                # Increment count
                existing.order_count += 1
                existing.last_ordered = datetime.now()
            else:
                # Add new favorite
                profile.favorite_orders.append(
                    FavoriteOrder(
                        restaurant=order.restaurant,
                        food_item=order.food_item,
                        last_ordered=datetime.now(),
                        order_count=1
                    )
                )

            # Keep only top 10 favorites (sorted by count)
            profile.favorite_orders.sort(key=lambda x: x.order_count, reverse=True)
            profile.favorite_orders = profile.favorite_orders[:10]

        # Save profile
        return self.save_user_profile(profile)

    def update_preferences(self, uid: str, preferences: dict) -> bool:
        """
        Update user preferences from memory trigger

        Args:
            uid: User ID
            preferences: Dict with favorite_cuisines, favorite_restaurants, dietary_preferences

        Returns:
            True if successful
        """
        profile = self.get_user_profile(uid)

        # Merge new preferences (avoid duplicates)
        if "favorite_restaurants" in preferences:
            for restaurant in preferences["favorite_restaurants"]:
                if restaurant not in profile.favorite_restaurants:
                    profile.favorite_restaurants.append(restaurant)

        if "dietary_preferences" in preferences:
            for pref in preferences["dietary_preferences"]:
                if pref not in profile.dietary_preferences:
                    profile.dietary_preferences.append(pref)

        return self.save_user_profile(profile)

    def get_session_context(self, session_id: str) -> dict:
        """
        Get temporary session context (for multi-turn conversations)

        Args:
            session_id: Session ID from Omi

        Returns:
            Dict with session context
        """
        key = f"session:{session_id}"

        try:
            if self.redis_client:
                data = self.redis_client.get(key)
                return json.loads(data) if data else {}
            else:
                return self.memory_store.get(key, {})
        except Exception as e:
            print(f"Error getting session context: {e}")
            return {}

    def save_session_context(self, session_id: str, context: dict, ttl: int = 3600) -> bool:
        """
        Save session context (expires after TTL)

        Args:
            session_id: Session ID
            context: Dict to save
            ttl: Time to live in seconds (default 1 hour)

        Returns:
            True if successful
        """
        key = f"session:{session_id}"

        try:
            if self.redis_client:
                self.redis_client.setex(key, ttl, json.dumps(context))
            else:
                self.memory_store[key] = context

            return True

        except Exception as e:
            print(f"Error saving session context: {e}")
            return False
