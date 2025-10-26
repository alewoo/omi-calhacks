"""
FoodVoice - Voice-activated food ordering for Omi
Main FastAPI application
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from models import RealtimeWebhook, MemoryCreated, OrderResult
from services import (
    IntentParser,
    StorageService,
    OrderService,
    OmiNotificationService,
    RestaurantLookupService
)

# Load environment variables
load_dotenv()

# Initialize services (will be set up in lifespan)
intent_parser = None
storage = None
order_service = None
notification_service = None
restaurant_lookup = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    global intent_parser, storage, order_service, notification_service, restaurant_lookup

    print("🚀 Starting FoodVoice API...")

    # Initialize all services
    intent_parser = IntentParser()
    storage = StorageService()
    order_service = OrderService()
    notification_service = OmiNotificationService()
    restaurant_lookup = RestaurantLookupService()

    print("✅ All services initialized")
    print(f"🔑 Omi API Key: {os.getenv('OMI_API_KEY')[:20]}...")
    print(f"🤖 Claude API: {'✓' if os.getenv('ANTHROPIC_API_KEY') else '✗'}")
    print(f"🤖 MultiOn API: {'✓' if os.getenv('MULTION_API_KEY') else '✗ (using deep links)'}")

    yield

    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="FoodVoice API",
    description="Voice-activated food ordering for Omi wearable",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "app": "FoodVoice",
        "version": "1.0.0",
        "endpoints": {
            "realtime": "/webhook/transcript",
            "memory": "/webhook/memory",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "intent_parser": intent_parser is not None,
            "storage": storage is not None,
            "order_service": order_service is not None,
            "notification_service": notification_service is not None,
            "restaurant_lookup": restaurant_lookup is not None,
        },
        "config": {
            "claude_api": bool(os.getenv("ANTHROPIC_API_KEY")),
            "omi_api": bool(os.getenv("OMI_API_KEY")),
            "multion_api": bool(os.getenv("MULTION_API_KEY")),
        }
    }


@app.post("/webhook/transcript")
async def handle_realtime_transcript(webhook: RealtimeWebhook):
    """
    Handle real-time transcript from Omi device

    This is called continuously as the user speaks
    """

    try:
        # Extract user speech
        user_text = webhook.get_user_text()

        if not user_text:
            return {"status": "no_speech", "message": "No user speech detected"}

        print(f"📝 Transcript: {user_text}")

        # Parse for food ordering intent
        order_intent = intent_parser.parse_food_order(user_text)

        if not order_intent:
            return {
                "status": "no_intent",
                "message": "No food order detected"
            }

        print(f"🍕 Order intent detected: {order_intent.food_item}")
        print(f"   Restaurant: {order_intent.restaurant or 'Any'}")
        print(f"   Confidence: {order_intent.confidence}")

        # Get session context to extract uid (or use a default for testing)
        session_context = storage.get_session_context(webhook.session_id)
        uid = session_context.get("uid", "test_user")

        # Handle "order my usual"
        if order_intent.quick_order:
            profile = storage.get_user_profile(uid)

            if profile.last_order:
                print("🔄 Quick order: using last order")
                order_intent = profile.last_order
            else:
                # No previous order
                await notification_service.send_notification(
                    uid,
                    "I don't have a previous order saved yet. Please tell me what you'd like!"
                )
                return {
                    "status": "no_previous_order",
                    "message": "No previous order found"
                }

        # Look up restaurant if not specified
        if not order_intent.restaurant:
            restaurant_info = restaurant_lookup.find_restaurant(
                order_intent.food_item,
                order_intent.cuisine
            )
            if restaurant_info:
                order_intent.restaurant = restaurant_info.name
                print(f"🔍 Found restaurant: {restaurant_info.name} (rating: {restaurant_info.rating})")
        else:
            # Get restaurant info for existing restaurant
            restaurant_info = restaurant_lookup.find_restaurant(
                order_intent.food_item,
                order_intent.cuisine
            )

        # Estimate price
        if restaurant_info:
            price_estimate = restaurant_lookup.estimate_price(order_intent.food_item, restaurant_info)
        else:
            price_estimate = "$15-25"

        # Generate order summary
        summary = order_service.get_order_summary(order_intent)
        print(f"📋 Order summary: {summary}")

        # Send voice confirmation first (mimics real confirmation flow)
        restaurant_name = order_intent.restaurant or "a highly rated restaurant"
        await notification_service.send_order_confirmation_voice(
            uid,
            restaurant=restaurant_name,
            food_item=order_intent.food_item,
            price=price_estimate
        )

        # Place order
        result = order_service.place_order(order_intent)

        # Save as last order
        storage.save_last_order(uid, order_intent)

        # Send final confirmation with link
        await notification_service.send_order_confirmation(
            uid,
            summary,
            result.deep_link
        )

        return {
            "status": "success",
            "order": order_intent.model_dump(),
            "result": result.model_dump(),
            "message": f"Order placed: {summary}"
        }

    except Exception as e:
        print(f"❌ Error handling transcript: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/memory")
async def handle_memory_created(webhook: MemoryCreated):
    """
    Handle memory creation webhook - extract food preferences

    This is called after a conversation is completed and saved as a memory
    """

    try:
        print(f"🧠 Memory created for user: {webhook.uid}")

        # Extract full conversation text
        conversation = webhook.memory.transcript

        if not conversation:
            return {"status": "no_transcript"}

        # Extract food preferences from conversation
        preferences = intent_parser.extract_preferences(conversation)

        print(f"📊 Extracted preferences: {preferences}")

        # Update user profile
        if any(preferences.values()):
            storage.update_preferences(webhook.uid, preferences)

            # Send notification about learned preferences
            if preferences.get("favorite_restaurants"):
                restaurants = ", ".join(preferences["favorite_restaurants"][:3])
                await notification_service.send_notification(
                    webhook.uid,
                    f"I learned you like: {restaurants}! I'll remember that for next time."
                )

        return {
            "status": "success",
            "preferences": preferences
        }

    except Exception as e:
        print(f"❌ Error handling memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/profile/{uid}")
async def get_user_profile(uid: str):
    """Get user profile (for debugging)"""
    profile = storage.get_user_profile(uid)
    return profile.model_dump()


@app.post("/profile/{uid}/setup")
async def setup_user_profile(uid: str, request: Request):
    """
    Setup user profile (for initial configuration)

    Body:
    {
        "delivery_address": "123 Main St, City, ST 12345",
        "phone": "+1234567890",
        "favorite_restaurants": ["Pizza Hut", "Chipotle"],
        "dietary_preferences": ["vegetarian"]
    }
    """

    try:
        data = await request.json()

        profile = storage.get_user_profile(uid)

        # Update fields
        if "delivery_address" in data:
            profile.delivery_address = data["delivery_address"]
        if "phone" in data:
            profile.phone = data["phone"]
        if "favorite_restaurants" in data:
            profile.favorite_restaurants = data["favorite_restaurants"]
        if "dietary_preferences" in data:
            profile.dietary_preferences = data["dietary_preferences"]

        # Save
        storage.save_user_profile(profile)

        return {
            "status": "success",
            "profile": profile.model_dump()
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all exceptions"""
    print(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))

    print(f"🚀 Starting server on port {port}...")
    print(f"📖 Docs: http://localhost:{port}/docs")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
