# Complete Testing & Setup Guide for FoodVoice

## 🔗 Your Deployed App

**Webhook URL:**
```
https://alexwang409--foodvoice-omi-fastapi-app.modal.run/webhook/transcript
```

**Modal Dashboard (CHECK THIS FOR LOGS):**
```
https://modal.com/apps/alexwang409/main/deployed/foodvoice-omi
```

---

## 1. View Live Logs (MOST IMPORTANT FOR DEBUGGING)

### Option A: Modal Web Dashboard (EASIEST)
1. Go to: https://modal.com/apps/alexwang409/main/deployed/foodvoice-omi
2. Click "App Logs" tab
3. You'll see real-time logs with emojis showing what's happening:
   - 📝 Transcript received
   - ✓ Keywords matched
   - 🍕 Order detected
   - ❌ Errors

### Option B: Terminal
```bash
modal app logs foodvoice-omi
```

---

## 2. Test Your Webhook Locally

### Quick Health Check
```bash
curl https://alexwang409--foodvoice-omi-fastapi-app.modal.run/health | python3 -m json.tool
```

Should show:
```json
{
  "status": "healthy",
  "services": {
    "intent_parser": true,
    "storage": true
  }
}
```

### Test Order Intent
```bash
curl -X POST https://alexwang409--foodvoice-omi-fastapi-app.modal.run/webhook/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test123",
    "segments": [{
      "text": "I want to order a pepperoni pizza",
      "speaker": "User",
      "speaker_id": 0,
      "is_user": true,
      "start": 0.0,
      "end": 2.5
    }]
  }'
```

### Test "Order My Usual"
First, place an order (above). Then:
```bash
curl -X POST https://alexwang409--foodvoice-omi-fastapi-app.modal.run/webhook/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test456",
    "segments": [{
      "text": "order my usual",
      "speaker": "User",
      "speaker_id": 0,
      "is_user": true,
      "start": 0.0,
      "end": 1.5
    }]
  }'
```

---

## 3. Register in Omi App

### On Your Phone:

1. Open **Omi app**
2. Go to **"App Store"** tab (bottom navigation)
3. Tap **"Submit App"** or **"+"** button

4. **Fill in form:**

   **App Name:**
   ```
   FoodVoice
   ```

   **Description:**
   ```
   Voice-activated food ordering. Say "order a pizza" or "order my usual" - AI handles the rest!
   ```

   **Team Name:**
   ```
   [Your Team Name]
   ```

   **App Capabilities:**
   - ✅ Select **"External Integration"**

   **Trigger Event:**
   - ✅ Select **"Transcript Processed"** (NOT "Audio Bytes"!!!)
   - ⚠️ CRITICAL: If you select "Audio Bytes", the app will NOT work!

   **Webhook URL:**
   ```
   https://alexwang409--foodvoice-omi-fastapi-app.modal.run/webhook/transcript
   ```

   **Import Permissions (OPTIONAL - leave OFF for now):**
   - Create conversations: OFF
   - Create memories: OFF
   - Read conversations: OFF
   - Read memories: OFF

5. **Tap "Submit App"**

6. Your app should appear in your account immediately!

---

## 4. Test with Omi Device

### Setup
1. Make sure Omi DevKit 2 is paired with your phone
2. Open Omi app → verify device is connected
3. Make sure your new app (FoodVoice) is enabled

### Test Commands

**Test 1: Basic Order**
Say clearly to device:
> "I want to order a pepperoni pizza"

**Test 2: Specific Restaurant**
> "Order a burger from Five Guys"

**Test 3: Cuisine Type**
> "Order Chinese food"

**Test 4: Quick Reorder**
> "Order my usual"

### What to Look For
1. **Device captures your voice** ✓
2. **Check Modal logs** for:
   - 📝 Transcript: [your words]
   - ✓ Matched keywords: ['order', 'pizza']
   - ✓ Food intent detected
   - 🍕 Order intent detected: pepperoni pizza
3. **Response** should include:
   - Order summary
   - DoorDash deep link

---

## 5. Debugging Tips

### If "no_intent" Response

**Check Modal logs first!** This will tell you exactly what's happening.

Go to: https://modal.com/apps/alexwang409/main/deployed/foodvoice-omi

Look for:
- "⚠️ No food keywords found" → Intent parser didn't recognize food words
- "❌ Error parsing intent" → Claude API issue
- "✓ Matched keywords" → Good! Intent was detected

### If Claude API Errors

Check your Modal secret has the correct API key:
```bash
modal secret list
```

Should show `foodvoice-secrets`

### If No Response at All

1. Check webhook URL is correct in Omi app
2. Verify device is connected and speaking
3. Check Modal logs for any requests coming in

---

## 6. Demo Script for CalHacks

### 60-Second Demo

**Setup (5 sec):**
*Hold up Omi device*
> "I have the Omi DevKit 2 paired and ready."

**Demo 1: Voice Order (25 sec):**
*Say to device:* "I want to order a pepperoni pizza"
*Show Modal logs on laptop*
> "Watch the logs - it heard my voice, matched the keywords 'order' and 'pizza', sent to Claude AI for parsing, and generated the order!"

**Demo 2: Show Response (15 sec):**
*Show the JSON response*
> "It detected I want pepperoni pizza, would find nearby restaurants, and send me a DoorDash link to complete checkout."

**Demo 3: Quick Reorder (15 sec):**
*Say:* "Order my usual"
> "It remembered my last order! Instant reordering for busy people."

**Wow Moment:**
> "All hands-free - perfect for ordering while driving, cooking, or working. No menus, no tapping!"

---

## 7. Quick Commands Reference

### View Logs
```bash
modal app logs foodvoice-omi
```

### Redeploy After Changes
```bash
cd /Users/alexwang/cs/hackathons/omi/backend
modal deploy modal_app.py
```

### Test Locally First
```bash
cd /Users/alexwang/cs/hackathons/omi/backend
python main.py
# Server starts at http://localhost:8000
```

### Check Deployment Status
```bash
modal app list
```

---

## 8. Troubleshooting Checklist

- [ ] Modal app is deployed (check dashboard)
- [ ] Health endpoint returns "healthy"
- [ ] Modal secret `foodvoice-secrets` exists with API keys
- [ ] Omi app has correct webhook URL
- [ ] Omi device is paired and connected
- [ ] FoodVoice app is enabled in Omi app
- [ ] Test curl command works
- [ ] Modal logs show incoming requests

---

## 9. Key Files

- **Backend:** `/Users/alexwang/cs/hackathons/omi/backend/modal_app.py`
- **Test data:** `/Users/alexwang/cs/hackathons/omi/test_webhook.json`
- **This guide:** `/Users/alexwang/cs/hackathons/omi/TESTING_GUIDE.md`

---

## 10. For Judges/Demo

**What makes this special:**
1. **Voice-first:** No touch, no screens
2. **AI-powered:** Claude understands natural language
3. **Learning:** Remembers your preferences
4. **Fast:** 1 sentence = 1 order

**Tech stack:**
- Omi DevKit 2 hardware
- Claude AI for intent parsing
- FastAPI backend
- Modal serverless hosting
- DoorDash integration

---

**YOU'RE READY TO WIN! 🏆**

Next step: Register in Omi app, test with device, practice demo!
