"""Order placement service - handles DoorDash ordering"""
import os
from typing import Optional
from models.order import OrderIntent, OrderResult


class OrderService:
    """Handle food ordering via multiple methods"""

    def __init__(self):
        self.multion_key = os.getenv("MULTION_API_KEY")

    def place_order(self, order: OrderIntent) -> OrderResult:
        """
        Place food order using best available method

        Priority:
        1. MultiOn browser automation (if API key available)
        2. Deep link generation (fallback)

        Args:
            order: OrderIntent with order details

        Returns:
            OrderResult with status and details
        """

        # Try MultiOn first if available
        if self.multion_key:
            result = self._place_order_multion(order)
            if result.status == "success":
                return result

        # Fallback to deep link
        return self._generate_deeplink(order)

    def _place_order_multion(self, order: OrderIntent) -> OrderResult:
        """
        Use MultiOn to automate DoorDash ordering

        Args:
            order: OrderIntent

        Returns:
            OrderResult
        """
        try:
            # Import only if we have API key
            from multion import MultiOn

            multion = MultiOn(api_key=self.multion_key)

            # Build command for MultiOn
            if order.restaurant:
                command = f"Go to doordash.com, search for '{order.restaurant}', add '{order.food_item}' to cart, and go to checkout"
            else:
                command = f"Go to doordash.com, search for '{order.food_item}', pick the highest rated restaurant, add it to cart, and go to checkout"

            # Add dietary restrictions if any
            if order.dietary_restrictions:
                restrictions = ", ".join(order.dietary_restrictions)
                command += f" (filter for {restrictions} options)"

            # Execute automation
            response = multion.browse(
                cmd=command,
                url="https://www.doordash.com",
                max_steps=10
            )

            # Check if successful
            if response and hasattr(response, 'status'):
                return OrderResult(
                    status="success",
                    restaurant=order.restaurant or "Selected restaurant",
                    items=[order.food_item],
                    tracking_url="https://www.doordash.com/orders/"
                )

        except Exception as e:
            print(f"MultiOn error: {e}")

        # If MultiOn fails, fallback to deep link
        return self._generate_deeplink(order)

    def _generate_deeplink(self, order: OrderIntent) -> OrderResult:
        """
        Generate DoorDash deep link for manual ordering

        Args:
            order: OrderIntent

        Returns:
            OrderResult with deep link
        """

        # Build DoorDash search URL
        base_url = "https://www.doordash.com"

        if order.restaurant:
            # Search for specific restaurant
            restaurant_slug = order.restaurant.lower().replace(" ", "-")
            search_url = f"{base_url}/store/{restaurant_slug}/"

            # Try to add item to search
            if order.food_item:
                item_query = order.food_item.replace(" ", "%20")
                search_url += f"?query={item_query}"
        else:
            # General food search
            food_query = order.food_item.replace(" ", "%20")
            search_url = f"{base_url}/search/?query={food_query}"

            # Add cuisine filter if available
            if order.cuisine:
                cuisine_query = order.cuisine.replace(" ", "%20")
                search_url += f"&cuisine={cuisine_query}"

        return OrderResult(
            status="pending",
            restaurant=order.restaurant or f"Search: {order.food_item}",
            items=[order.food_item],
            deep_link=search_url
        )

    def get_order_summary(self, order: OrderIntent) -> str:
        """
        Generate human-readable order summary

        Args:
            order: OrderIntent

        Returns:
            String summary
        """
        parts = []

        if order.quick_order:
            parts.append("Your usual order")
        else:
            parts.append(order.food_item)

        if order.restaurant:
            parts.append(f"from {order.restaurant}")
        elif order.cuisine:
            parts.append(f"({order.cuisine} cuisine)")

        if order.dietary_restrictions:
            restrictions = ", ".join(order.dietary_restrictions)
            parts.append(f"[{restrictions}]")

        return " ".join(parts)
