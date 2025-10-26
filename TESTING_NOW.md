# 🎤 Testing Your Omi Device RIGHT NOW

## ✅ Current Status
- ✅ Server running at http://localhost:8000
- ✅ All services healthy (Claude AI, Storage, Order Service, etc.)
- ⏳ Need to expose server so Omi can reach it

---

## 🚀 Next Steps (5 minutes)

### Step 1: Expose Server with ngrok (2 min)

**In a NEW terminal window:**

```bash
# Start ngrok
ngrok http 8000
```

You'll see output like:
```
Session Status                online
Account                       [your account]
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
```

**Copy that `https://abc123.ngrok.io` URL!** (yours will be different)

Keep this terminal window open!

---

### Step 2: Register App in Omi (3 min)

**On your phone with Omi app:**

1. Open **Omi mobile app**
2. Tap **App Store** (bottom tab)
3. Tap **"+"** or **"Submit App"** or **"Create App"**
4. Fill in:

```
App Name: FoodVoice

Description: Order food by voice from any restaurant.
Say "order a pizza" or "order my usual" - AI handles the rest.

Real-time Webhook URL:
https://YOUR-NGROK-URL.ngrok.io/webhook/transcript

Memory Webhook URL:
https://YOUR-NGROK-URL.ngrok.io/webhook/memory

(Replace YOUR-NGROK-URL with your actual ngrok URL)
```

5. **Submit**

---

### Step 3: Test with Your Device!

**Say to your Omi device:**

> "Order a pepperoni pizza from Domino's"

**Watch your terminal** where the server is running. You should see:
```
📝 Transcript: Order a pepperoni pizza from Domino's
🍕 Order intent detected: pepperoni pizza
🔍 Found restaurant: Domino's Pizza (rating: 4.2)
📋 Order summary: pepperoni pizza from Domino's Pizza
```

**On your phone:** You'll get a notification with order details and a DoorDash link!

---

## 🐛 Troubleshooting

### ngrok asks for authentication
If ngrok says "Authenticate", run:
```bash
ngrok config add-authtoken YOUR_TOKEN
```

Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken

### Server not receiving requests
Check:
1. ngrok terminal is still running
2. Server terminal is still running
3. Webhook URL in Omi app is correct (should end with `/webhook/transcript`)

### View server logs in real-time
```bash
tail -f /tmp/omi_server.log
```

---

## 📋 Quick Tests

### Test 1: Basic Order
**Say:** "Order a pepperoni pizza from Domino's"
**Expected:** Order confirmation + DoorDash link

### Test 2: Quick Reorder
**Say:** "Order my usual"
**Expected:** Retrieves last order + confirms

### Test 3: Dietary Filter
**Say:** "Order a vegetarian burger"
**Expected:** Parses dietary restriction + finds restaurant

---

## 🎬 Demo Script (if testing works)

Once you confirm it's working, use this for judges:

**Demo 1 (25 sec):**
Say: "Order a pepperoni pizza from the closest highly rated place"
Show: Voice confirmation + phone with DoorDash link

**Demo 2 (15 sec):**
Say: "Order my usual"
Show: Quick reorder works

**Wow moment (15 sec):**
Show: Server logs with order history learning

---

## ⚡ Super Quick Alternative (if ngrok is problematic)

Deploy to Modal instead (takes 10 min):

```bash
pip install modal
modal setup
modal deploy modal_deploy.py
```

You'll get a permanent URL instead of ngrok.

---

**CURRENT NEXT STEP:** Open a new terminal and run `ngrok http 8000`
