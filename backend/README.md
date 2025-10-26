# FoodVoice - Voice Food Ordering for Omi

Voice-activated food delivery app for the Omi wearable device. Order DoorDash with natural language and have it learn your preferences over time.

## 🎯 Features

- ✅ Voice-activated food ordering ("Order a pizza")
- ✅ AI intent parsing using Claude
- ✅ Quick re-orders ("Order my usual")
- ✅ Learns food preferences over time
- ✅ Deep link fallback for easy checkout
- ✅ MultiOn browser automation (optional)

## 🛠️ Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Required keys:
- `ANTHROPIC_API_KEY` - Your Claude API key (already filled in)
- `OMI_API_KEY` - Your Omi API key (already filled in)

Optional:
- `MULTION_API_KEY` - For browser automation (can skip for MVP)
- `REDIS_URL` - Redis connection (defaults to localhost)

### 3. Start Redis (Optional)

If you don't have Redis, the app will use in-memory storage (fine for demo):

```bash
# macOS
brew install redis
brew services start redis

# Or use Docker
docker run -d -p 6379:6379 redis:alpine
```

### 4. Run Locally

```bash
cd backend
python main.py
```

Server will start at `http://localhost:8000`

View docs at `http://localhost:8000/docs`

## 🚀 Deploy to Modal

### 1. Install Modal

```bash
pip install modal
modal setup  # Follow prompts to authenticate
```

### 2. Create Modal Secrets

Go to [modal.com](https://modal.com) → Secrets → Create new secret named `foodvoice-secrets`

Add these keys:
- `ANTHROPIC_API_KEY`
- `OMI_API_KEY`
- `REDIS_URL` (optional)
- `MULTION_API_KEY` (optional)

### 3. Deploy

```bash
modal deploy modal_deploy.py
```

You'll get a webhook URL like: `https://your-app.modal.run`

## 📱 Register with Omi

1. Open the Omi app on your phone
2. Go to **App Store → Submit App**
3. Fill in:
   - **Name**: FoodVoice
   - **Description**: Order food by voice, learns your preferences
   - **Webhook URL**: `https://your-modal-url.modal.run/webhook/transcript`
   - **Memory Webhook**: `https://your-modal-url.modal.run/webhook/memory`

## 🧪 Testing

### Test Intent Parsing

```bash
curl -X POST http://localhost:8000/webhook/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test123",
    "segments": [
      {
        "text": "Order a pepperoni pizza from Dominos",
        "speaker": "User",
        "speaker_id": 0,
        "is_user": true,
        "start": 0.0,
        "end": 2.5
      }
    ]
  }'
```

### Test "Order My Usual"

```bash
# First order
curl -X POST http://localhost:8000/webhook/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test123",
    "segments": [{
      "text": "Order a burger from Five Guys",
      "speaker": "User",
      "speaker_id": 0,
      "is_user": true,
      "start": 0.0,
      "end": 2.0
    }]
  }'

# Then test quick order
curl -X POST http://localhost:8000/webhook/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test123",
    "segments": [{
      "text": "Order my usual",
      "speaker": "User",
      "speaker_id": 0,
      "is_user": true,
      "start": 0.0,
      "end": 1.0
    }]
  }'
```

### Check User Profile

```bash
curl http://localhost:8000/profile/test_user
```

## 🎤 Demo Script for Judges

**Setup**: Show Omi app connected to your device

**Demo 1 - Basic Order**:
- Say: "Order a pepperoni pizza from Domino's"
- Show: AI parsing → order confirmation → deep link sent

**Demo 2 - Quick Reorder**:
- Say: "Order my usual"
- Show: Retrieves last order → places same order

**Demo 3 - Learning**:
- Show user profile with saved preferences
- Explain: "It learned I like pepperoni pizza and will suggest it next time"

**Wow Moment**:
- "This saves 2 minutes every lunch. No more tapping through menus while driving!"

## 📁 Project Structure

```
backend/
├── main.py                     # FastAPI app + webhook endpoints
├── modal_deploy.py             # Modal deployment config
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── models/
│   ├── __init__.py
│   ├── omi_webhook.py         # Omi webhook data models
│   └── order.py               # Order intent & user profile models
└── services/
    ├── __init__.py
    ├── intent_parser.py       # Claude-powered intent parsing
    ├── storage.py             # Redis storage service
    ├── order_service.py       # DoorDash order placement
    └── omi_notifications.py   # Send notifications to Omi
```

## 🐛 Troubleshooting

**Redis connection failed**:
- App will fallback to in-memory storage automatically
- Fine for demo, but data won't persist between restarts

**Intent parsing not working**:
- Check `ANTHROPIC_API_KEY` is set correctly
- Check API key has credits
- Look at console logs for detailed errors

**MultiOn not working**:
- Skip it! Deep links work great for demo
- DoorDash will open on user's phone with pre-filled cart

**Omi notifications not sending**:
- Check `OMI_API_KEY` is correct
- Verify app is registered in Omi App Store
- App prints "[DEMO MODE]" if keys are missing (still works for testing)

## 🏆 Winning Tips

1. **Practice your demo script** - 60 seconds, smooth, no errors
2. **Have backup orders ready** - Pre-configure 2-3 test orders
3. **Show the "learning"** - Pull up user profile to show saved preferences
4. **Emphasize voice UX** - "Hands-free ordering while driving/cooking"
5. **Have deep links ready** - If MultiOn fails, deep links always work

## 📧 Questions?

Check the main CalHacks guide or reach out on Slack!
