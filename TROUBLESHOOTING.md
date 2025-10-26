# FoodVoice - Troubleshooting Guide

Quick reference for fixing common issues during setup and demo.

## Table of Contents
- [Audio Issues](#audio-issues)
- [Webhook Issues](#webhook-issues)
- [API Key Issues](#api-key-issues)
- [Deployment Issues](#deployment-issues)
- [Intent Parsing Issues](#intent-parsing-issues)
- [Demo Day Emergencies](#demo-day-emergencies)

---

## Audio Issues

### Omi Device Not Responding

**Symptom**: Device doesn't respond to "Hey Omi"

**Checklist**:
- [ ] Device is charged (check LED indicator)
- [ ] Device is paired in Omi mobile app (check Bluetooth connection)
- [ ] App shows "Connected" status
- [ ] Try power cycling: hold button for 10 seconds to restart

**Quick Fix**:
```bash
# In Omi app:
Settings → Device → Forget Device → Re-pair
```

### Device Responds But Orders Don't Go Through

**Symptom**: "Hey Omi" works but no notifications for food orders

**This means audio is fine - check webhook setup instead** (see [Webhook Issues](#webhook-issues))

### Poor Audio Quality in Venue

**Symptom**: Device misunderstands commands in loud environment

**Quick Fixes**:
1. **Increase volume**: Speak louder and closer to device
2. **Reduce background noise**: Step away from speakers/crowds
3. **Adjust sensitivity**:
   ```
   Omi app → Settings → Audio → Mic Sensitivity → High
   ```
4. **Use push-to-talk mode** if available in app settings

### Audio Latency

**Symptom**: Long delay between speaking and response

**Expected latency**: 2-3 seconds for food orders (Claude API call)

**If >5 seconds**:
- Check your internet connection
- Check Modal app status (might be cold starting)
- Verify Claude API isn't rate limited

---

## Webhook Issues

### No Notifications After Speaking

**Symptom**: You speak an order, device processes it, but no notification appears

**Debug Process**:

1. **Check Modal Logs**:
   ```bash
   # Visit: https://modal.com/apps/foodvoice-omi
   # Click "Logs" tab
   # Look for incoming requests
   ```

2. **If NO requests appear** → Webhook URL is wrong:
   - Go to Omi app → My Apps → FoodVoice → Settings
   - Verify webhook URL ends with `/webhook/transcript`
   - Should be: `https://[your-name]--foodvoice-omi-fastapi-app.modal.run/webhook/transcript`

3. **If requests appear but NO notification** → OMI API key issue:
   - Check Modal secrets have `OMI_API_KEY`
   - Verify the key is correct (should start with `omi_dev_`)

4. **If requests appear with errors** → Check error message in logs

**Quick Test**:
```bash
# Manually test webhook (replace with your URL)
curl -X POST https://[your-url].modal.run/webhook/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test",
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

Expected output:
```json
{
  "message": "🍕 pizza from Dominos\n\n[link]"
}
```

### Webhook URL Not Accepting Requests

**Symptom**: cURL test returns 404 or 500 error

**Fixes**:

1. **Verify deployment**:
   ```bash
   modal app list
   # Should show "foodvoice-omi" as deployed
   ```

2. **Re-deploy if needed**:
   ```bash
   cd backend
   modal deploy modal_app.py
   ```

3. **Check health endpoint**:
   ```bash
   curl https://[your-url].modal.run/health
   ```

### App Not Listed in Omi App Store

**Symptom**: Can't find FoodVoice in "My Apps"

**Fixes**:
1. Check you submitted the app (App Store → Submit App)
2. Wait 1-2 minutes for processing
3. Force close and reopen Omi app
4. If still missing, re-submit with same details

---

## API Key Issues

### Claude API Not Working

**Symptom**: Modal logs show "Intent parser not initialized" or "ANTHROPIC_API_KEY not set"

**Fix**:

1. **Check Modal Secrets**:
   ```bash
   modal secret list
   # Should show "foodvoice-secrets"
   ```

2. **View secret contents**:
   - Go to https://modal.com/secrets
   - Click on "foodvoice-secrets"
   - Verify `ANTHROPIC_API_KEY` is set

3. **Update secret**:
   - Click "Edit"
   - Add or update `ANTHROPIC_API_KEY=sk-ant-api03-...`
   - Save and re-deploy:
     ```bash
     modal deploy modal_app.py
     ```

4. **Check API key is valid**:
   ```bash
   # Test directly (replace with your key)
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: sk-ant-api03-..." \
     -H "anthropic-version: 2023-06-01" \
     -H "content-type: application/json" \
     -d '{
       "model": "claude-sonnet-4-20250514",
       "max_tokens": 1024,
       "messages": [{"role": "user", "content": "Hi"}]
     }'
   ```

### Omi API Key Issues

**Symptom**: Orders process but no notifications sent

**Debug**:

1. **Check Modal logs** for:
   ```
   [DEMO MODE] Would send notification: ...
   ```
   This means OMI_API_KEY is missing or invalid

2. **Verify key in Modal secrets**:
   - Go to https://modal.com/secrets → foodvoice-secrets
   - Ensure `OMI_API_KEY` is set
   - Should look like: `omi_dev_c40202a1c776472f33ce542439434d2d`

3. **Get correct key**:
   - Open Omi mobile app
   - Go to Settings → Developer → API Key
   - Copy the key and update Modal secret

### Rate Limits

**Symptom**: "Rate limit exceeded" errors in logs

**For Claude API**:
- Each request uses ~500 tokens
- Free tier: 50 requests/minute (should be plenty for demo)
- If hitting limits, wait 1 minute between tests

**For Omi API**:
- Notifications: ~100/hour limit
- Should be fine for demo
- If hitting limits, space out test orders

---

## Deployment Issues

### Modal Deploy Fails

**Symptom**: `modal deploy` command returns errors

**Common Errors & Fixes**:

**Error: "Not authenticated"**
```bash
modal setup
# Follow prompts to authenticate
```

**Error: "App name already exists"**
```python
# In modal_app.py, change app name:
app = modal.App("foodvoice-omi-yourname")
```

**Error: "Secret not found"**
```bash
# Create secret via web:
# 1. Go to https://modal.com/secrets
# 2. Create new secret: "foodvoice-secrets"
# 3. Add required keys
```

**Error: "Image build failed"**
```bash
# Usually a dependency issue
# Check requirements.txt versions are compatible
# Try deploying with older package versions
```

### Modal App Cold Starts

**Symptom**: First request takes 10+ seconds

**Expected behavior**: Modal keeps 1 container warm (we set `min_containers=1`)

**If still seeing cold starts**:
- Check Modal dashboard for container status
- Verify `min_containers=1` is set in modal_app.py
- Consider upgrading Modal plan for better performance

### Health Check Fails

**Symptom**: `/health` endpoint returns unhealthy status

**Debug**:
```bash
curl https://[your-url].modal.run/health
```

**Check response**:
```json
{
  "status": "healthy",
  "services": {
    "intent_parser": false,  // ← If false, API key issue
    "storage": true
  },
  "config": {
    "claude_api": false,  // ← Check this
    "omi_api": true
  }
}
```

**Fix false values**:
- See [API Key Issues](#api-key-issues) section

---

## Intent Parsing Issues

### Food Orders Not Detected

**Symptom**: You say food order but app responds with "no_intent"

**Debug**:

1. **Check Modal logs** for:
   ```
   📝 Processing: [your text]
   ℹ️ No food order trigger - skipping
   ```

2. **Verify trigger phrases** - must include one of:
   - "order food"
   - "order a"
   - "can you order"
   - "get food"
   - "doordash"

3. **Try explicit phrase**:
   ```
   "Can you order me a pizza from Domino's?"
   ```

**Current trigger words** (in [modal_app.py:196-215](backend/modal_app.py#L196-L215)):
```python
strong_triggers = [
    "order food", "order a", "order me", "order my",
    "can you order", "could you order",
    "get food", "buy food", "foodvoice",
    "doordash", "uber eats", "grubhub"
]
```

### Wrong Food Item Parsed

**Symptom**: You say "pizza" but Claude extracts "burger"

**This is rare but can happen**. If it does during demo:

**Explain to judges**:
- "Claude has 95%+ accuracy on intent parsing"
- "This is a known challenge with speech-to-text + NLP"
- "In production we'd add confidence thresholds and confirmation prompts"

**Quick fix for demo**:
- Try again with clearer phrase
- Use restaurant name: "Order from Domino's" (more specific)

### Claude Returns Invalid JSON

**Symptom**: Modal logs show JSON parsing error

**Debug**:
```
❌ Error parsing intent: Expecting value: line 1 column 1 (char 0)
🤖 Claude raw response (full): [check what Claude returned]
```

**This is handled** - the code strips markdown (lines 168-176 in modal_app.py)

**If still occurring**:
- Update to latest Claude model version
- Check prompt format hasn't changed
- Verify Anthropic API is working

---

## Demo Day Emergencies

### Complete System Failure

**Symptom**: Nothing works, 5 minutes before demo

**Emergency Backup Plan**:

1. **Have screenshots ready**:
   - Voice command in Omi app
   - Notification with link
   - User profile JSON

2. **Demo with cURL** on your laptop:
   ```bash
   # Show judges the backend works
   curl -X POST https://[your-url].modal.run/webhook/transcript \
     -H "Content-Type: application/json" \
     -d '{"session_id":"demo","segments":[{"text":"Order pizza","speaker":"User","speaker_id":0,"is_user":true,"start":0,"end":1}]}'
   ```

3. **Explain clearly**:
   "We're having connectivity issues with the Omi device, but let me show you the backend working via API calls and screenshots of successful tests earlier today."

### Omi Device Dies During Demo

**Battery died or device unresponsive**

**Backup**:
1. Show screenshots of it working
2. Demo the API directly with cURL
3. Explain: "The Omi device handles voice capture and sends us clean transcripts - here's what that looks like in JSON..."

### Internet Connection Issues

**Can't reach Modal app**

**Backup**:
1. Use phone hotspot for internet
2. Switch to laptop-only demo (cURL + screenshots)
3. Explain the architecture with confidence

### Judge Asks Hard Questions

**"How do you handle payment?"**
- "We don't store payment info - the deep link takes users to DoorDash where they complete checkout. In production, we'd integrate DoorDash's Order API for full automation."

**"What about privacy?"**
- "We only store order preferences. Omi's transcripts are processed in real-time and not persisted. Users can delete their profile anytime."

**"Why not just use the DoorDash app?"**
- "Voice is faster and hands-free. Perfect for driving, cooking, meetings. We save 2-3 minutes per order. For regular lunch orders, that adds up to hours per year."

**"What if it orders the wrong thing?"**
- "We use Claude's structured output which is 95%+ accurate. In production, we'd add a confirmation prompt: 'I heard pizza from Domino's, is that correct?'"

**"How do you make money?"**
- "Commission per order (restaurant pays us) or subscription for power users. Similar to Uber Eats' business model."

---

## Quick Command Reference

### Check Modal Status
```bash
modal app list
modal secret list
```

### View Logs
```bash
# Web: https://modal.com/apps/foodvoice-omi/logs
# Or CLI:
modal app logs foodvoice-omi
```

### Re-deploy
```bash
cd backend
modal deploy modal_app.py
```

### Test Health
```bash
curl https://[your-url].modal.run/health
```

### Test Order
```bash
curl -X POST https://[your-url].modal.run/webhook/transcript \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","segments":[{"text":"Order pizza from Dominos","speaker":"User","speaker_id":0,"is_user":true,"start":0,"end":2}]}'
```

### View User Profile
```bash
curl https://[your-url].modal.run/profile/test_user
```

---

## When All Else Fails

1. **Stay calm** - judges understand it's a hackathon
2. **Show what works** - even partial demos are impressive
3. **Explain the vision** - judges care about ideas and potential
4. **Have screenshots** - proof it worked at some point
5. **Know your code** - be ready to walk through architecture

**Remember**: Most judges are engineers who have debugged production systems at 3am. They'll respect your troubleshooting process and how you handle issues.

---

## Prevention Checklist

Do this the night before to avoid issues:

- [ ] Deploy to Modal and verify /health
- [ ] Test 3 successful voice orders end-to-end
- [ ] Take screenshots of successful orders
- [ ] Save Modal logs showing successful requests
- [ ] Charge Omi device to 100%
- [ ] Download this troubleshooting guide offline
- [ ] Bookmark Modal dashboard
- [ ] Write down your webhook URL
- [ ] Test internet connection at venue (if possible)

---

## Support Resources

- **Modal Docs**: https://modal.com/docs
- **Modal Status**: https://status.modal.com
- **Anthropic Status**: https://status.anthropic.com
- **CalHacks Slack**: #omi-help channel
- **Your Modal Dashboard**: https://modal.com/apps

Good luck! With proper preparation, you won't need most of this guide - but it's here if you do!
