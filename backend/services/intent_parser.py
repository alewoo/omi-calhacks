"""Intent parsing using Claude API"""
import json
import os
from anthropic import Anthropic
from typing import Optional
from models.order import OrderIntent


class IntentParser:
    """Parse food ordering intent from natural language using Claude"""

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def parse_food_order(self, text: str) -> Optional[OrderIntent]:
        """
        Parse food order intent from voice transcript

        Args:
            text: User's voice transcript

        Returns:
            OrderIntent if food order detected, None otherwise
        """

        # First check if this is food-related
        if not self._is_food_intent(text):
            return None

        # Parse detailed order information
        prompt = f"""
You are a food ordering assistant. Parse this voice command into structured order data.

Voice command: "{text}"

Extract:
1. food_item: What specific food they want (e.g., "pepperoni pizza", "burger", "pad thai")
2. restaurant: Specific restaurant name if mentioned (or null)
3. cuisine: Type of cuisine if mentioned (e.g., "Italian", "Chinese", "Mexican")
4. dietary_restrictions: List any dietary needs (e.g., ["vegetarian"], ["gluten-free"])
5. quick_order: true if they said "my usual", "same as last time", "regular order"
6. delivery_instructions: Any special delivery notes
7. confidence: 0-1 score of how confident you are in this parse

Return ONLY valid JSON in this exact format:
{{
  "food_item": "string or null",
  "restaurant": "string or null",
  "cuisine": "string or null",
  "dietary_restrictions": [],
  "quick_order": false,
  "delivery_instructions": "string or null",
  "confidence": 0.95
}}
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=500,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse JSON response
            result = json.loads(response.content[0].text)

            # Convert to OrderIntent model
            return OrderIntent(
                food_item=result.get("food_item") or "",
                restaurant=result.get("restaurant"),
                cuisine=result.get("cuisine"),
                dietary_restrictions=result.get("dietary_restrictions", []),
                quick_order=result.get("quick_order", False),
                delivery_instructions=result.get("delivery_instructions"),
                confidence=result.get("confidence", 0.0)
            )

        except Exception as e:
            print(f"Error parsing intent: {e}")
            return None

    def _is_food_intent(self, text: str) -> bool:
        """Quick check if text contains food ordering keywords"""
        text_lower = text.lower()

        food_keywords = [
            "order", "get me", "i want", "food", "hungry",
            "pizza", "burger", "sushi", "chinese", "italian",
            "restaurant", "delivery", "doordash", "uber eats",
            "usual", "lunch", "dinner", "breakfast"
        ]

        return any(keyword in text_lower for keyword in food_keywords)

    def extract_preferences(self, conversation: str) -> dict:
        """
        Extract food preferences from a conversation (for memory trigger)

        Args:
            conversation: Full conversation transcript

        Returns:
            Dict with favorite_cuisines, favorite_restaurants, dietary_preferences
        """

        prompt = f"""
Analyze this conversation and extract the person's food preferences.

Conversation:
{conversation}

Extract:
1. favorite_cuisines: List of cuisines they like (e.g., ["Italian", "Thai"])
2. favorite_restaurants: Specific restaurants mentioned positively
3. dietary_preferences: Any dietary restrictions or preferences (e.g., ["vegetarian", "no dairy"])
4. favorite_dishes: Specific dishes they enjoyed or ordered

Return ONLY valid JSON:
{{
  "favorite_cuisines": [],
  "favorite_restaurants": [],
  "dietary_preferences": [],
  "favorite_dishes": []
}}
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=500,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )

            return json.loads(response.content[0].text)

        except Exception as e:
            print(f"Error extracting preferences: {e}")
            return {
                "favorite_cuisines": [],
                "favorite_restaurants": [],
                "dietary_preferences": [],
                "favorite_dishes": []
            }
