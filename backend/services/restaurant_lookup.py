"""Restaurant lookup service - find restaurants and pricing"""
from typing import Optional, List
from anthropic import Anthropic
import json
import os


class RestaurantInfo:
    """Restaurant information"""
    def __init__(self, name: str, rating: float, cuisine: str, price_range: str):
        self.name = name
        self.rating = rating
        self.cuisine = cuisine
        self.price_range = price_range  # e.g., "$", "$$", "$$$"


class RestaurantLookupService:
    """
    Look up restaurants using AI (for MVP/demo)

    In production, you'd use:
    - Google Places API
    - Yelp API
    - DoorDash merchant API
    """

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # Mock database for demo (pre-populate with local favorites)
        self.mock_restaurants = {
            "pizza": [
                RestaurantInfo("Domino's Pizza", 4.2, "Pizza", "$$"),
                RestaurantInfo("Pizza Hut", 4.0, "Pizza", "$$"),
                RestaurantInfo("Little Caesars", 3.8, "Pizza", "$"),
            ],
            "burger": [
                RestaurantInfo("Five Guys", 4.5, "Burgers", "$$"),
                RestaurantInfo("In-N-Out Burger", 4.7, "Burgers", "$"),
                RestaurantInfo("Shake Shack", 4.4, "Burgers", "$$"),
            ],
            "chinese": [
                RestaurantInfo("Panda Express", 4.0, "Chinese", "$"),
                RestaurantInfo("P.F. Chang's", 4.3, "Chinese", "$$$"),
            ],
            "mexican": [
                RestaurantInfo("Chipotle", 4.2, "Mexican", "$$"),
                RestaurantInfo("Taco Bell", 3.9, "Mexican", "$"),
            ],
            "sushi": [
                RestaurantInfo("Kura Sushi", 4.4, "Sushi", "$$"),
                RestaurantInfo("Sushi House", 4.2, "Sushi", "$$"),
            ],
        }

    def find_restaurant(
        self,
        food_item: str,
        cuisine: Optional[str] = None,
        max_price: str = "$$$"
    ) -> Optional[RestaurantInfo]:
        """
        Find best restaurant for food item

        Args:
            food_item: What they want (e.g., "pepperoni pizza")
            cuisine: Cuisine type if specified
            max_price: Max price range

        Returns:
            RestaurantInfo or None
        """

        # Determine category from food item
        category = self._categorize_food(food_item)

        if category in self.mock_restaurants:
            restaurants = self.mock_restaurants[category]

            # Filter by price
            price_levels = {"$": 1, "$$": 2, "$$$": 3}
            max_level = price_levels.get(max_price, 3)
            restaurants = [r for r in restaurants if price_levels.get(r.price_range, 1) <= max_level]

            # Sort by rating
            restaurants.sort(key=lambda x: x.rating, reverse=True)

            # Return highest rated
            return restaurants[0] if restaurants else None

        # Fallback: use AI to suggest
        return self._ai_suggest_restaurant(food_item, cuisine)

    def _categorize_food(self, food_item: str) -> str:
        """Categorize food item into cuisine type"""
        food_lower = food_item.lower()

        if any(word in food_lower for word in ["pizza", "pepperoni", "margherita"]):
            return "pizza"
        elif any(word in food_lower for word in ["burger", "cheeseburger"]):
            return "burger"
        elif any(word in food_lower for word in ["chinese", "fried rice", "lo mein", "orange chicken"]):
            return "chinese"
        elif any(word in food_lower for word in ["burrito", "taco", "quesadilla"]):
            return "mexican"
        elif any(word in food_lower for word in ["sushi", "sashimi", "roll"]):
            return "sushi"

        return "general"

    def _ai_suggest_restaurant(self, food_item: str, cuisine: Optional[str]) -> Optional[RestaurantInfo]:
        """Use AI to suggest a restaurant"""

        prompt = f"What's a highly-rated chain restaurant that serves {food_item}"
        if cuisine:
            prompt += f" ({cuisine} cuisine)"
        prompt += "? Just give me the restaurant name."

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )

            name = response.content[0].text.strip()
            return RestaurantInfo(name, 4.3, cuisine or "Various", "$$")

        except Exception as e:
            print(f"Error suggesting restaurant: {e}")
            return None

    def estimate_price(self, food_item: str, restaurant: RestaurantInfo) -> str:
        """
        Estimate price for food item

        Args:
            food_item: Food item
            restaurant: Restaurant info

        Returns:
            Price string (e.g., "$15-20")
        """

        # Simple price estimation based on restaurant price range
        price_ranges = {
            "$": (8, 12),
            "$$": (12, 20),
            "$$$": (20, 35),
        }

        low, high = price_ranges.get(restaurant.price_range, (15, 25))

        return f"${low}-${high}"
