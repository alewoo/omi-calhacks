# 🚀 Deploy to Modal - Step by Step

Your server is working locally! Now let's deploy it to Modal for a permanent public URL.

---

## Step 1: Setup Modal Account (3 min)

**In your terminal:**

```bash
cd /Users/alexwang/cs/hackathons/omi/backend
modal setup
```

This will:
1. Open your browser to https://modal.com
2. Ask you to sign up/login (use GitHub - it's fastest)
3. Generate an authentication token
4. Save it automatically

**Just follow the prompts!**

---

## Step 2: Create Modal Secret (2 min)

**In your browser:**

1. Go to https://modal.com/secrets
2. Click **"Create Secret"**
3. Name it: `foodvoice-secrets`
4. Add these key-value pairs:

```
ANTHROPIC_API_KEY = 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

OMI_API_KEY = omi_dev_c40202a1c776472f33ce542439434d2d
```

5. Click **"Create"**

---

## Step 3: Deploy Your App (1 min)

**In your terminal:**

```bash
cd /Users/alexwang/cs/hackathons/omi/backend
modal deploy modal_deploy.py
```

You'll see output like:
```
✓ Created objects.
├── 🔨 Created mount /Users/alexwang/cs/hackathons/omi/backend
└── 🔨 Created fastapi_app => https://yourname--foodvoice-omi.modal.run
```

**Copy that URL!** Example: `https://yourname--foodvoice-omi.modal.run`

---

## Step 4: Test Your Deployed App (30 sec)

**In your terminal:**

```bash
# Test health endpoint (replace with YOUR actual URL)
curl https://yourname--foodvoice-omi.modal.run/health
```

You should see:
```json
{
  "status": "healthy",
  "services": {
    "intent_parser": true,
    "storage": true,
    ...
  }
}
```

---

## Step 5: Register in Omi App (2 min)

**On your phone:**

1. Open **Omi app**
2. Go to **App Store** (bottom tab)
3. Tap **"+"** or **"Submit App"**
4. Fill in:

```
App Name: FoodVoice

Description: Order food by voice. Say "order a pizza"
or "order my usual" - AI handles the rest.

Team Name: [Your Name]

Real-time Webhook:
https://YOUR-MODAL-URL.modal.run/webhook/transcript

Memory Webhook:
https://YOUR-MODAL-URL.modal.run/webhook/memory
```

5. **Submit**

---

## Step 6: TEST WITH YOUR OMI DEVICE! 🎤

**Say to your Omi device:**

> "Order a pepperoni pizza from Domino's"

**Watch your Modal logs:**

```bash
modal logs foodvoice-omi
```

You should see:
```
📝 Transcript: Order a pepperoni pizza from Domino's
🍕 Order intent detected: pepperoni pizza
🔍 Found restaurant: Domino's Pizza (rating: 4.2)
```

**On your phone:** You'll get a notification with order details!

---

## 🎬 Demo Script (Once Working)

### Demo 1: Natural Voice Order (25 sec)
**Say:** "Order a pepperoni pizza from the closest highly rated place"
- Show device captures voice
- Show notification confirms order
- Show phone with DoorDash link

### Demo 2: Quick Reorder (15 sec)
**Say:** "Order my usual"
- Show it retrieves last order
- Show confirmation

### Demo 3: Wow Moment (15 sec)
**Show:** User profile endpoint
```bash
curl https://YOUR-URL.modal.run/profile/test_user
```
- Show favorite orders tracked
- Show order count
- Explain: "It's learning my preferences!"

---

## 🐛 Troubleshooting

### "Secret not found" error
Make sure you:
1. Named the secret exactly `foodvoice-secrets`
2. Added both API keys
3. Try deploying again: `modal deploy modal_deploy.py`

### Check logs
```bash
# View live logs
modal logs foodvoice-omi

# View recent logs
modal logs foodvoice-omi --history 100
```

### Redeploy after changes
```bash
# Make a change to code
modal deploy modal_deploy.py

# It will update the existing deployment
```

### Test webhook directly
```bash
curl -X POST https://YOUR-URL.modal.run/webhook/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test123",
    "segments": [{
      "text": "Order a pizza",
      "speaker": "User",
      "speaker_id": 0,
      "is_user": true,
      "start": 0.0,
      "end": 1.5
    }]
  }'
```

---

## 📊 Check Deployment Status

**In Modal dashboard:**
- Go to https://modal.com/apps
- Click on `foodvoice-omi`
- See live metrics, logs, and requests

---

## ⚡ Quick Commands Reference

```bash
# Setup Modal (first time only)
modal setup

# Deploy/update app
modal deploy modal_deploy.py

# View logs
modal logs foodvoice-omi

# Stop app (if needed)
modal app stop foodvoice-omi

# List all apps
modal app list
```

---

## 🏆 You're Ready!

Once you complete these steps, you'll have:
- ✅ Permanent public URL (no ngrok needed!)
- ✅ Deployed app that judges can test anytime
- ✅ Live logs to debug
- ✅ Ready for demo

---

**START HERE:** Run `modal setup` in your terminal!

After setup completes, run `modal deploy modal_deploy.py`
