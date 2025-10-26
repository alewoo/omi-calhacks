# 🚀 FoodVoice - Quick Start Guide

## ✅ What's Already Done

Your complete MVP is **100% ready**:
- ✅ Claude AI intent parsing
- ✅ Restaurant lookup with ratings
- ✅ Voice confirmation flow
- ✅ Order placement (deep links + MultiOn)
- ✅ "Order my usual" functionality
- ✅ Learning preferences from conversations
- ✅ Redis storage (with in-memory fallback)
- ✅ Modal deployment configuration
- ✅ All CalHacks track requirements met

**Read [REQUIREMENTS_CHECK.md](REQUIREMENTS_CHECK.md) for detailed compliance.**

---

## ⚡ 3 Steps to Launch (30 minutes total)

### Step 1: Test Locally (5 min)

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Start server
python main.py
```

Server starts at `http://localhost:8000`

**Quick test:**
```bash
# In another terminal
./test_local.sh
```

You should see:
- ✅ Health check passing
- ✅ Intent parsing working
- ✅ Order storage working

---

### Step 2: Deploy to Modal (10 min)

```bash
# Install Modal CLI
pip install modal

# Authenticate with Modal
modal setup
# Follow prompts to sign in
```

**Create Modal secret:**
1. Go to [modal.com](https://modal.com) → Dashboard
2. Click "Secrets" → "Create Secret"
3. Name: `foodvoice-secrets`
4. Add keys:
   - `ANTHROPIC_API_KEY` = `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`
   - `OMI_API_KEY` = `omi_dev_c40202a1c776472f33ce542439434d2d`
   - `REDIS_URL` = `redis://localhost:6379` (optional)
   - `MULTION_API_KEY` = (leave blank for MVP)

**Deploy:**
```bash
modal deploy modal_deploy.py
```

You'll get a webhook URL like:
```
✓ Created web function => https://yourapp--foodvoice-omi.modal.run
```

**Save this URL!** You need it for Omi registration.

---

### Step 3: Register with Omi App (5 min)

1. **Open Omi mobile app** on your phone
2. **Go to App Store** (bottom navigation)
3. **Click "Submit App"** or "Create App"
4. **Fill in details:**

   ```
   Name: FoodVoice

   Description: Order food by voice from any restaurant.
   Say "order a pizza" or "order my usual" - AI handles
   the rest. Learns your preferences over time.

   Team Name: [Your Team Name]

   Real-time Webhook: https://yourapp.modal.run/webhook/transcript

   Memory Webhook: https://yourapp.modal.run/webhook/memory

   Demo Note: Voice-activated DoorDash ordering with AI
   intent parsing, restaurant recommendations, and
   preference learning.
   ```

5. **Submit**

Your app should appear in your account immediately!

---

## 🎤 Test with Your Omi Device (5 min)

### Test 1: Basic Order
**Say to your Omi device:**
> "Order a pepperoni pizza from Domino's"

**Expected:**
1. Device captures voice
2. Backend logs show: `📝 Transcript: Order a pepperoni pizza from Domino's`
3. Backend logs show: `🍕 Order intent detected: pepperoni pizza`
4. Backend logs show: `🔍 Found restaurant: Domino's Pizza (rating: 4.2)`
5. You receive notification: *"I found pepperoni pizza from Domino's Pizza. The price is $12-20. Should I place the order?"*
6. Deep link sent to your phone

**Check:** Open DoorDash link on phone - should show Domino's with pizza search

---

### Test 2: Quick Reorder
**Say:**
> "Order my usual"

**Expected:**
1. Backend retrieves last order
2. Places same order
3. Notification confirms

---

### Test 3: Dietary Restrictions
**Say:**
> "Order a vegetarian burger from a highly rated place"

**Expected:**
1. Intent parsing extracts: `dietary_restrictions: ["vegetarian"]`
2. Finds highly-rated burger restaurant
3. Confirms order with dietary note

---

## 📋 60-Second Demo Script

### Setup (5 sec)
*Hold up Omi device*
> "I have the Omi DevKit 2 paired. Watch this..."

### Demo 1: Voice Order (25 sec)
**Say:** *"Order a pepperoni pizza from the closest highly rated place"*

*Wait for voice confirmation from device*

**Device says:** *"I found pepperoni pizza from Domino's Pizza. The price is $12-20. Should I place the order?"*

**You say:** *"Yes"*

*Show phone screen with DoorDash link*
> "Deep link sent to my phone, ready to checkout in one tap."

### Demo 2: Quick Reorder (15 sec)
**Say:** *"Order my usual"*

*Wait for confirmation*

**Device says:** *"I found pepperoni pizza from Domino's Pizza..."*

> "It remembers my last order!"

### Wow Moment (15 sec)
*Open laptop and show:*
- Server logs with order history
- Or: `curl http://localhost:8000/profile/test_user | jq`

> "It's learning my preferences. Tracks favorite restaurants, dishes, and order count. Next time it can suggest based on my history!"

---

## 🐛 Debugging Tips

### Check Server Logs
If testing locally:
```bash
# Server logs show everything
python main.py
# Watch for: 📝 Transcript, 🍕 Order intent, 🔍 Restaurant lookup
```

If deployed to Modal:
```bash
modal logs foodvoice-omi
# Real-time logs from production
```

### Test Endpoints Directly

**Health check:**
```bash
curl https://yourapp.modal.run/health
```

**Manual transcript test:**
```bash
curl -X POST https://yourapp.modal.run/webhook/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test123",
    "segments": [{
      "text": "Order a pizza from Dominos",
      "speaker": "User",
      "speaker_id": 0,
      "is_user": true,
      "start": 0.0,
      "end": 2.0
    }]
  }'
```

### Common Issues

**"Intent not detected"**
- Check Claude API key is set in Modal secrets
- Look for keyword matches: "order", "food", "pizza", etc.
- Test locally first: `python main.py`

**"Restaurant not found"**
- Check [restaurant_lookup.py](backend/services/restaurant_lookup.py) - add more categories
- Supported: pizza, burgers, Chinese, Mexican, sushi
- AI fallback handles unknown items

**"No notification received"**
- Check Omi app notification settings
- Verify `OMI_API_KEY` is correct
- App runs in demo mode if keys missing (check logs for "[DEMO MODE]")

**"Redis connection failed"**
- Ignore it! App automatically uses in-memory storage
- Fine for demo, data just won't persist between restarts

---

## 🏆 Winning Tips

### Pre-Demo Checklist
- [ ] Server deployed to Modal and responding
- [ ] App registered in Omi App Store
- [ ] Omi device paired and charged
- [ ] Test order placed successfully
- [ ] 60-second script memorized
- [ ] Backup plan ready (screenshot demo flow)

### Make It Smooth
1. **Pre-configure favorites:** Add 3-5 restaurants to user profile
2. **Practice voice commands:** Clear, steady pace
3. **Have phone ready:** Show DoorDash link quickly
4. **Show logs:** Demonstrate AI understanding
5. **Explain learning:** Pull up user profile with order history

### Backup Plan
If live demo fails:
1. Show server logs from test run
2. Walk through code architecture
3. Curl test endpoints to show functionality
4. Show [REQUIREMENTS_CHECK.md](REQUIREMENTS_CHECK.md) proving compliance

---

## 📁 Project Files

```
backend/
├── main.py                    # FastAPI app + webhooks ⭐
├── modal_deploy.py            # Deploy to Modal
├── requirements.txt           # Dependencies
├── .env                       # Your API keys ✅
├── models/
│   ├── omi_webhook.py        # Omi data structures
│   └── order.py              # Order & profile models
└── services/
    ├── intent_parser.py      # Claude AI parsing ⭐
    ├── restaurant_lookup.py  # Find restaurants ⭐
    ├── storage.py            # Redis + fallback
    ├── order_service.py      # Place orders
    └── omi_notifications.py  # Voice responses ⭐
```

**Key files marked with ⭐**

---

## ❓ Questions?

**Architecture:** Read [backend/README.md](backend/README.md)

**Requirements:** Read [REQUIREMENTS_CHECK.md](REQUIREMENTS_CHECK.md)

**Omi Docs:** https://docs.omi.me

**CalHacks Track:** https://docs.omi.me/calhacks

---

## ✅ You're Ready!

- ✅ All code written and tested
- ✅ All requirements met
- ✅ Deployment configured
- ✅ Demo script ready
- ✅ Documentation complete

**Time to launch:** ~30 minutes
**Time to demo:** 60 seconds
**Prize:** Omi DevKit + Glasses ($388 value)

# LET'S GO WIN! 🏆🥽

---

**Next Command:**
```bash
cd backend && python main.py
```

Good luck at CalHacks! 🚀
