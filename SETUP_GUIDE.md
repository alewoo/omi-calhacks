# FoodVoice - Complete Setup Guide for CalHacks

This guide will walk you through setting up FoodVoice from scratch for the CalHacks demo.

## Table of Contents
1. [Quick Start (15 minutes)](#quick-start)
2. [Detailed Setup](#detailed-setup)
3. [Testing Your Setup](#testing-your-setup)
4. [Omi App Submission](#omi-app-submission)
5. [Troubleshooting](#troubleshooting)

---

## Quick Start

If you're short on time, here's the bare minimum to get running:

```bash
# 1. Navigate to backend
cd backend

# 2. Install dependencies (if not already done)
pip install -r requirements.txt

# 3. Your .env file already has API keys - verify they're correct
cat .env

# 4. Deploy to Modal
modal deploy modal_app.py

# 5. Get your webhook URL (will be printed after deploy)
# Should look like: https://alexwang409--foodvoice-omi-fastapi-app.modal.run

# 6. Submit app in Omi mobile app with this webhook URL
# 7. Test by saying: "Order a pepperoni pizza from Domino's"
```

**Expected time**: 15 minutes

---

## Detailed Setup

### Step 1: Verify Your Environment

Check that you have everything installed:

```bash
# Check Python version (need 3.9+)
python3 --version

# Check if Modal is installed
modal --version

# If modal not installed:
pip install modal
```

### Step 2: Authenticate with Modal

If this is your first time using Modal:

```bash
# This will open a browser for authentication
modal setup
```

Follow the prompts to:
1. Create a Modal account (or sign in)
2. Authorize the CLI

### Step 3: Configure Secrets in Modal

Your app needs API keys to work. You have two options:

#### Option A: Use Modal Secrets (Recommended for production)

1. Go to https://modal.com/secrets
2. Click "Create New Secret"
3. Name it: `foodvoice-secrets`
4. Add these key-value pairs:

```
ANTHROPIC_API_KEY=sk-ant-api03-[your-key-here]
OMI_API_KEY=omi_dev_c40202a1c776472f33ce542439434d2d
BRIGHT_DATA_API_KEY=[optional]
```

5. Save the secret

#### Option B: Use Existing Secrets (Quick)

Your secrets might already be configured. Check by running:

```bash
modal secret list
```

If you see `foodvoice-secrets`, you're good to go!

### Step 4: Deploy to Modal

From the `/backend` directory:

```bash
# Deploy the app
modal deploy modal_app.py
```

You should see output like:
```
✓ Created objects.
├── 🔨 Created mount /Users/alexwang/cs/hackathons/omi/backend
├── 🔨 Created function fastapi_app.
└── 🔨 Created ASGI app => https://alexwang409--foodvoice-omi-fastapi-app.modal.run
✓ App deployed! 🎉

View Deployment: https://modal.com/apps/[your-workspace]/foodvoice-omi
```

**Important**: Copy that HTTPS URL - you'll need it for Omi!

### Step 5: Verify Deployment

Test that your backend is running:

```bash
# Check health endpoint
curl https://[your-url].modal.run/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "intent_parser": true,
    "storage": true
  },
  "config": {
    "claude_api": true,
    "omi_api": true
  }
}
```

If you see any `false` values, check your Modal secrets!

### Step 6: Configure Your Omi Device

#### Physical Setup
1. **Charge the device**: Ensure it's at least 80% charged
2. **Pair with phone**:
   - Open Omi mobile app
   - Follow pairing instructions (Bluetooth)
   - Confirm you see "Connected" status

#### Test Audio
1. Say "Hey Omi" - device should respond
2. Ask a simple question: "What time is it?"
3. Check that responses come through clearly

### Step 7: Submit Your App to Omi App Store

This is how you connect your webhook to Omi:

1. **Open Omi mobile app**
2. **Navigate**: Tap menu → "App Store" → "Submit App"
3. **Fill in the form**:
   - **App Name**: FoodVoice
   - **Description**: Voice-activated food ordering that learns your preferences
   - **Category**: Productivity (or Food & Dining if available)
   - **Webhook URL**: `https://[your-url].modal.run/webhook/transcript`
   - **Memory Webhook URL**: `https://[your-url].modal.run/webhook/memory`
   - **Icon URL** (optional): Leave blank for now
   - **Author**: Your name
   - **Team Name**: Your team name (or just your name)

4. **Submit**: Tap "Submit App"

5. **Activate**: After submission, go to "My Apps" and toggle FoodVoice ON

### Step 8: Test End-to-End

Now test the full flow:

#### Test 1: Basic Order

1. **Say to your Omi device**:
   ```
   "Order a pepperoni pizza from Domino's"
   ```

2. **Wait 2-3 seconds**

3. **Check your Omi app**: You should see a notification like:
   ```
   🍕 pepperoni pizza from Domino's

   [Link to DoorDash]
   ```

4. **Click the link**: Should open Google search that redirects to DoorDash

#### Test 2: Quick Reorder

1. **Say to your Omi device**:
   ```
   "Order my usual"
   ```

2. **Check notification**: Should be the same pizza order

#### Test 3: Check Saved Data

Visit in your browser:
```
https://[your-url].modal.run/profile/test_user
```

You should see JSON with your last order saved.

---

## Testing Your Setup

### Manual Testing with cURL

If voice testing isn't working, test the webhook directly:

```bash
# Test a basic order
curl -X POST https://[your-url].modal.run/webhook/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
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

Expected response:
```json
{
  "message": "🍕 pepperoni pizza from Dominos\n\n[DoorDash link]"
}
```

### Check Modal Logs

If something goes wrong, check the logs:

1. Go to https://modal.com/apps
2. Click on "foodvoice-omi"
3. Click on "Logs" tab
4. Look for errors or debug output

You should see lines like:
```
📝 Processing: Order a pepperoni pizza from Dominos
✓ Food order trigger detected
🤖 Claude raw response (full): {"food_item": "pepperoni pizza", ...}
🍕 Order intent detected: pepperoni pizza
```

### Common Test Phrases

Test these phrases to verify your app works:

✅ **Should work**:
- "Order a burger from Five Guys"
- "Order pad thai from Thai Kitchen"
- "Order sushi"
- "Order my usual" (after placing first order)
- "Can you order me a pizza from Pizza Hut?"

❌ **Should NOT trigger** (by design):
- "I like food" (no order intent)
- "What's your favorite order?" (question, not command)
- "Food is great" (random mention)

---

## Omi App Submission

### Submission Form Details

When filling out the Omi app submission form, here's what to include:

**App Name**: FoodVoice

**Short Description** (for app store listing):
```
Order food by voice, hands-free. Learns your preferences and makes reordering instant.
```

**Long Description**:
```
FoodVoice turns your Omi device into a voice-activated food ordering assistant.

Features:
• Order from DoorDash using natural language
• Quick reorders: just say "order my usual"
• Learns your favorite restaurants and meals
• Hands-free ordering while driving, cooking, or working

Perfect for:
- Busy professionals who order lunch regularly
- Anyone who wants to save time on food delivery
- People who prefer voice over typing

Just speak your order, and FoodVoice handles the rest!
```

**Webhook URLs**:
- **Transcript Webhook**: `https://[your-modal-url].modal.run/webhook/transcript`
- **Memory Webhook**: `https://[your-modal-url].modal.run/webhook/memory`

**Demo Notes** (for judges):
```
Say "Order a pepperoni pizza from Domino's" to test.

The app will:
1. Parse your intent using Claude AI
2. Generate a DoorDash link
3. Send a notification with the link

Then say "Order my usual" to see it remember your order!
```

### After Submission

1. **Check "My Apps"**: You should see FoodVoice listed
2. **Toggle it ON**: Make sure the switch is enabled
3. **Test immediately**: Say an order to verify webhooks are connected

---

## Troubleshooting

### Issue: Modal deploy fails

**Symptoms**: Error messages during `modal deploy`

**Fixes**:
1. Check you're authenticated: `modal token set --token-id ... --token-secret ...`
2. Verify the Modal app name isn't taken by someone else
3. Try changing the app name in [modal_app.py](backend/modal_app.py):
   ```python
   app = modal.App("foodvoice-omi-yourname")  # Add your name
   ```

### Issue: Health endpoint returns false for services

**Symptoms**: `/health` shows `"intent_parser": false`

**Fixes**:
1. Check Modal secrets are configured correctly
2. Go to https://modal.com/secrets
3. Verify `foodvoice-secrets` exists and has ANTHROPIC_API_KEY
4. Re-deploy: `modal deploy modal_app.py`

### Issue: Omi not hearing voice commands

**Symptoms**: Device doesn't respond when you speak

**Fixes**:
1. Check device is paired and connected in app
2. Test with "Hey Omi" - should respond
3. Check battery level (low battery = poor mic sensitivity)
4. Reduce background noise
5. Speak louder and clearer
6. Check mic permissions on your phone

### Issue: No notification appears after speaking

**Symptoms**: You say an order, but no notification shows up

**Debug steps**:
1. Check Modal logs for incoming requests
2. If no requests appear → webhook URL wrong in Omi app
3. If requests appear but no notification → check OMI_API_KEY in secrets
4. Test webhook manually with cURL (see testing section)

**Fixes**:
- Verify webhook URL in Omi app settings (should end with `/webhook/transcript`)
- Ensure app is toggled ON in "My Apps"
- Check OMI_API_KEY is correct in Modal secrets
- Try re-submitting the app with correct webhook URL

### Issue: Wrong intent parsed

**Symptoms**: You say "pizza" but it thinks you said "burger"

**This is actually okay for the demo!** Explain to judges:
- "This is using Claude for intent parsing, which is 95%+ accurate"
- "With more training data, we'd improve accuracy"
- "The important part is the architecture works end-to-end"

### Issue: Deep link doesn't work

**Symptoms**: Clicking the notification link doesn't open DoorDash

**Explanation**: Google's "I'm Feeling Lucky" redirects can sometimes fail due to rate limits or geo-blocking.

**Fixes**:
- Explain to judges: "In production, we'd use DoorDash's official API or cache store URLs"
- Show that the link generation logic still works (it creates a valid Google search)
- Have screenshots ready of successful orders

### Issue: "Order my usual" says no previous order

**Symptoms**: Second order doesn't remember first order

**Fixes**:
1. Check that storage service is initialized (see Modal logs)
2. Ensure you're using same user ID (currently hardcoded as "test_user")
3. Verify first order actually went through (check `/profile/test_user`)

---

## Performance Tips for Demo Day

### Before Your Demo Slot

1. **Test the full flow 3 times** in the hour before your slot
2. **Check venue noise levels** - might need to adjust mic sensitivity
3. **Have Modal logs open** on your laptop so you can debug live
4. **Take screenshots** of successful orders as backup
5. **Charge Omi device** to 100%

### During Your Demo

1. **Speak clearly** - venue might be loud
2. **Wait 2-3 seconds** after speaking for processing
3. **Show judges your phone** so they see notification pop up
4. **Have backup phrases ready** in case one fails:
   - "Order a burger from Five Guys"
   - "Order sushi from Sushi Palace"
   - "Order my usual"

### If Something Goes Wrong

1. **Stay calm** - judges know it's a hackathon
2. **Have screenshots** ready to show it working
3. **Explain the issue** - "Looks like we hit a rate limit, but here's what it does..."
4. **Test with cURL** on your laptop to show the backend works

---

## Pre-Demo Checklist

Print this and check off each item before your demo:

**24 Hours Before**:
- [ ] Modal app deployed and /health returns healthy
- [ ] Test order placed successfully via voice
- [ ] Screenshots taken of successful orders
- [ ] This guide read through completely

**1 Hour Before**:
- [ ] Omi device charged to 100%
- [ ] Tested 3 different order phrases successfully
- [ ] Modal logs open in browser tab
- [ ] Demo script reviewed

**5 Minutes Before**:
- [ ] Test "Hey Omi" works in venue
- [ ] Omi app open on phone
- [ ] Deep breath - you got this!

---

## Next Steps After Setup

Once everything is working:

1. **Practice your demo script** (see [DEMO_SCRIPT.md](DEMO_SCRIPT.md))
2. **Test edge cases** to anticipate judge questions
3. **Prepare your pitch** - 90 seconds, tight and compelling
4. **Get sleep** - you'll demo better when rested!

---

## Additional Resources

- **Modal Docs**: https://modal.com/docs
- **Omi API Docs**: Check the Omi app for documentation links
- **Anthropic Claude API**: https://docs.anthropic.com/
- **Your backend README**: [backend/README.md](backend/README.md)
- **Demo Script**: [DEMO_SCRIPT.md](DEMO_SCRIPT.md)

---

## Questions?

If you run into issues not covered here:
1. Check Modal logs first (https://modal.com/apps/foodvoice-omi)
2. Review the troubleshooting section above
3. Test with cURL to isolate the issue
4. Ask on CalHacks Slack #omi-help channel

Good luck! You've got an awesome project - now go show it off!
