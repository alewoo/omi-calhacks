"""Send notifications back to Omi device"""
import os
import httpx
from typing import Optional


class OmiNotificationService:
    """Send notifications to Omi device"""

    def __init__(self):
        self.api_key = os.getenv("OMI_API_KEY")
        self.app_id = os.getenv("OMI_APP_ID")
        self.base_url = "https://api.omi.me"  # Update with actual Omi API base URL

    async def send_notification(
        self,
        uid: str,
        message: str,
        title: Optional[str] = None
    ) -> bool:
        """
        Send push notification to user's Omi device

        Args:
            uid: User ID
            message: Notification message
            title: Optional title

        Returns:
            True if successful
        """

        # TODO: Update with actual Omi notification API endpoint
        # This is a placeholder - check Omi docs for actual API

        if not self.api_key or not self.app_id:
            print(f"📱 [DEMO MODE] Would send notification: {message}")
            return True

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/notifications",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "X-App-ID": self.app_id
                    },
                    json={
                        "uid": uid,
                        "title": title or "Food Order",
                        "message": message
                    }
                )

                return response.status_code == 200

        except Exception as e:
            print(f"Error sending notification: {e}")
            return False

    async def send_order_confirmation(
        self,
        uid: str,
        order_summary: str,
        deep_link: Optional[str] = None
    ) -> bool:
        """
        Send order confirmation notification

        Args:
            uid: User ID
            order_summary: Human-readable order summary
            deep_link: Optional DoorDash link

        Returns:
            True if successful
        """

        message = f"✅ Order placed: {order_summary}"

        if deep_link:
            message += f"\n\nTap to complete checkout: {deep_link}"

        return await self.send_notification(uid, message, title="Order Confirmed")

    async def send_voice_response(self, uid: str, text: str) -> bool:
        """
        Send voice response back to device (text-to-speech)

        Args:
            uid: User ID
            text: Text to speak

        Returns:
            True if successful
        """

        # Omi supports voice output via notifications
        # The device will speak the message aloud

        return await self.send_notification(uid, text)

    async def send_order_confirmation_voice(
        self,
        uid: str,
        restaurant: str,
        food_item: str,
        price: str = "estimated $15-25"
    ) -> bool:
        """
        Send voice confirmation for order

        Args:
            uid: User ID
            restaurant: Restaurant name
            food_item: Food item ordered
            price: Price estimate

        Returns:
            True if successful
        """

        confirmation = (
            f"I found {food_item} from {restaurant}. "
            f"The price is {price}. "
            f"Should I place the order? Say yes to confirm or no to cancel."
        )

        return await self.send_voice_response(uid, confirmation)
