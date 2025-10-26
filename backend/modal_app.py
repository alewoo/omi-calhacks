"""
Complete Modal deployment with all code embedded
"""
import modal

# Create Modal app
app = modal.App("foodvoice-omi")

# Define container image with all dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "fastapi==0.109.0",
        "uvicorn[standard]==0.27.0",
        "pydantic==2.5.3",
        "pydantic-settings==2.1.0",
        "anthropic==0.18.1",
        "redis==5.0.1",
        "httpx==0.26.0",
        "python-dotenv==1.0.0",
    )
)

# Define secrets
secrets = [
    modal.Secret.from_name("foodvoice-secrets"),
]

@app.function(
    image=image,
    secrets=secrets,
    min_containers=1,
    timeout=300,
)
@modal.asgi_app()
def fastapi_app():
    """Complete FastAPI app embedded"""
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import JSONResponse
    from contextlib import asynccontextmanager
    import os
    from pydantic import BaseModel
    from typing import List, Optional
    from anthropic import Anthropic
    import json
    import httpx

    # Models
    class TranscriptSegment(BaseModel):
        text: str
        speaker: str
        speaker_id: int
        is_user: bool
        start: float
        end: float

    class RealtimeWebhook(BaseModel):
        session_id: str
        segments: List[TranscriptSegment]

        def get_user_text(self) -> str:
            # Get ALL text, not just is_user=True (Omi sometimes marks everything as is_user=False)
            return " ".join([s.text for s in self.segments])

    class OrderIntent(BaseModel):
        food_item: str
        restaurant: Optional[str] = None
        cuisine: Optional[str] = None
        dietary_restrictions: List[str] = []
        quick_order: bool = False
        delivery_instructions: Optional[str] = None
        confidence: float = 0.0

    # Services
    class IntentParser:
        def __init__(self):
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print("⚠️ WARNING: ANTHROPIC_API_KEY not set!")
            self.client = Anthropic(api_key=api_key)

        def parse_food_order(self, text: str) -> Optional[OrderIntent]:
            # Always try to parse if text mentions food - be permissive!
            if not self._is_food_intent(text):
                print(f"⚠️ No food keywords found in: {text}")
                return None

            print(f"✓ Food intent detected, parsing with Claude...")

            prompt = f"""
You are a food ordering assistant. Parse this voice command into structured order data.

Voice command: "{text}"

Extract:
1. food_item: What specific food they want
2. restaurant: Specific restaurant name if mentioned (or null)
3. cuisine: Type of cuisine if mentioned
4. dietary_restrictions: List any dietary needs
5. quick_order: true if they said "my usual", "same as last time"
6. delivery_instructions: Any special delivery notes
7. confidence: 0-1 score

Return ONLY valid JSON:
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
                    model="claude-sonnet-4-20250514",
                    max_tokens=500,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )

                # Debug: print the raw response
                response_text = response.content[0].text
                print(f"🤖 Claude raw response (full): {response_text}")

                # Strip markdown code blocks if present
                if response_text.strip().startswith("```"):
                    # Remove ```json at start and ``` at end
                    response_text = response_text.strip()
                    # Find the first { and last }
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}')
                    if start_idx != -1 and end_idx != -1:
                        response_text = response_text[start_idx:end_idx+1]
                    print(f"🔧 Stripped markdown, now: {response_text[:100]}")

                # Try to parse JSON
                result = json.loads(response_text)
                print(f"✓ Parsed order: {result.get('food_item', 'unknown')}")

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
                print(f"❌ Error parsing intent: {e}")
                print(f"❌ Response was: {response.content[0].text if 'response' in locals() else 'No response'}")
                return None

        def _is_food_intent(self, text: str) -> bool:
            text_lower = text.lower()

            # MUST have one of these strong trigger phrases
            strong_triggers = [
                "order food", "order a", "order me", "order my",
                "can you order", "could you order",  # Added conversational triggers
                "get food", "buy food", "foodvoice",
                "doordash", "uber eats", "grubhub"
            ]

            has_strong_trigger = any(trigger in text_lower for trigger in strong_triggers)

            if has_strong_trigger:
                print(f"✓ Food order trigger detected")
                return True

            # Don't trigger on random words like "order" or "food" alone
            print(f"ℹ️ No food order trigger - skipping")
            return False

    class StorageService:
        def __init__(self):
            self.memory_store = {}

        def save_last_order(self, uid: str, order: OrderIntent) -> bool:
            self.memory_store[f"last_order:{uid}"] = order.model_dump()
            return True

        def get_last_order(self, uid: str) -> Optional[OrderIntent]:
            data = self.memory_store.get(f"last_order:{uid}")
            if data:
                return OrderIntent(**data)
            return None

    # Initialize services immediately
    print("🚀 Starting FoodVoice API...")
    try:
        intent_parser = IntentParser()
        storage = StorageService()
        print("✅ All services initialized")
        print(f"🔑 API Keys - Claude: {bool(os.getenv('ANTHROPIC_API_KEY'))}, Omi: {bool(os.getenv('OMI_API_KEY'))}")
    except Exception as e:
        print(f"❌ Error initializing services: {e}")
        intent_parser = None
        storage = StorageService()

    # Create FastAPI app
    app = FastAPI(
        title="FoodVoice API",
        description="Voice-activated food ordering for Omi wearable",
        version="1.0.0",
    )

    @app.get("/")
    async def root():
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
        return {
            "status": "healthy",
            "services": {
                "intent_parser": intent_parser is not None,
                "storage": storage is not None,
            },
            "config": {
                "claude_api": bool(os.getenv("ANTHROPIC_API_KEY")),
                "omi_api": bool(os.getenv("OMI_API_KEY")),
            }
        }

    @app.post("/webhook/transcript")
    async def handle_realtime_transcript(webhook: RealtimeWebhook):
        try:
            # Debug: print raw webhook data
            print(f"🔍 Raw webhook received - session: {webhook.session_id}, segments: {len(webhook.segments)}")

            # Print each segment's details
            for i, seg in enumerate(webhook.segments):
                print(f"  Segment {i}: text='{seg.text}', is_user={seg.is_user}, speaker={seg.speaker}")

            user_text = webhook.get_user_text()
            print(f"📝 Extracted text: '{user_text}' (length: {len(user_text)})")

            if not user_text:
                print("⚠️ Empty transcript, skipping")
                return {"status": "no_speech"}

            print(f"📝 Processing: {user_text}")

            # Check if intent parser is available
            if intent_parser is None:
                print("❌ Intent parser not initialized")
                return {"status": "error", "message": "Intent parser not available"}

            # Parse for food ordering intent
            order_intent = intent_parser.parse_food_order(user_text)
            if not order_intent:
                print(f"ℹ️ No food order detected in: {user_text}")
                # DON'T send notification for non-food conversations
                return {"status": "no_intent"}

            print(f"🍕 Order intent detected: {order_intent.food_item}")

            uid = "test_user"  # Simple for now

            # Handle "order my usual"
            if order_intent.quick_order:
                last_order = storage.get_last_order(uid)
                if last_order:
                    print("🔄 Quick order: using last order")
                    order_intent = last_order
                else:
                    return {"status": "no_previous_order"}

            # Generate order summary
            restaurant = order_intent.restaurant or "a highly rated restaurant"
            summary = f"{order_intent.food_item} from {restaurant}"

            # Build DoorDash deep link
            food_query = order_intent.food_item.replace(" ", "%20")
            deep_link = f"https://www.doordash.com/search/?query={food_query}"

            # Save as last order
            storage.save_last_order(uid, order_intent)

            print(f"📋 Order placed: {summary}")
            print(f"🔗 Deep link: {deep_link}")

            # Prepare response with notification
            response_message = f"🍕 Order placed: {summary}. Check the link to complete checkout!\n\n{deep_link}"

            return {
                "status": "success",
                "order": order_intent.model_dump(),
                "deep_link": deep_link,
                "message": response_message
            }

        except Exception as e:
            print(f"❌ Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/webhook/memory")
    async def handle_memory_created(request: Request):
        try:
            data = await request.json()
            print(f"🧠 Memory created: {data.get('uid', 'unknown')}")
            return {"status": "success"}
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"status": "error", "message": str(e)}

    return app
