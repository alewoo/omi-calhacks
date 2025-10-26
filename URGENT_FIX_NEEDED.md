# URGENT: Omi App Configuration Issue

## Problem Detected

Your Omi app is **still sending binary audio data** instead of text transcripts to the webhook.

**Error in logs:**
```
RequestValidationError: Input should be a valid dictionary or object to extract fields from
Input: b'\x10\xff\xfc\xfe\x08\xff...' (binary audio bytes)
```

## What You Need to Do RIGHT NOW

### On Your Phone - Omi App:

1. Open **Omi mobile app**
2. Go to **Apps** tab (bottom navigation)
3. Find **FoodVoice** app (or whatever you named it)
4. Tap to **edit** the app
5. Under **Trigger Event**, you MUST select:
   - **"Transcript Processed"** (NOT "Audio Bytes")
6. Save the changes

### Why This Matters

- **Audio Bytes** = Raw binary audio data (what you're currently sending)
- **Transcript Processed** = Text that your backend can understand

Your backend expects JSON like this:
```json
{
  "session_id": "abc123",
  "segments": [
    {
      "text": "Order a pizza",
      "speaker": "User",
      "is_user": true,
      ...
    }
  ]
}
```

But it's receiving: `b'\x10\xff\xfc\xfe\x08\xff...'` (binary audio)

## After You Fix This

Test by saying to your Omi device:
> "Order a pepperoni pizza"

Then check the logs:
```bash
cd /Users/alexwang/cs/hackathons/omi/backend
modal app logs foodvoice-omi
```

You should see:
```
📝 Transcript: Order a pepperoni pizza
🍕 Order intent detected: pepperoni pizza
```

## Current Status

✅ Modal deployment: **WORKING**
✅ API health: **HEALTHY**
✅ Claude API: **CONNECTED**
✅ Intent detection: **FIXED (strict triggers only)**
❌ Omi app configuration: **NEEDS FIX** (wrong trigger type)

## Webhook URL (Correct)

```
https://alexwang409--foodvoice-omi-fastapi-app.modal.run/webhook/transcript
```

## Once Working

After you change the trigger to "Transcript Processed", the app will:
- ✅ Only respond to food ordering phrases
- ✅ No spam notifications for random conversations
- ✅ Send proper order confirmations with DoorDash links

---

**Action Required:** Change trigger to "Transcript Processed" in Omi app settings.
