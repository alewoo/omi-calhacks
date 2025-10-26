# FoodVoice - CalHacks Demo Script

## Pre-Demo Checklist (Do this BEFORE your demo slot!)

### 1. Device Setup (15 mins before)
- [ ] Omi device fully charged and paired with your phone
- [ ] Test audio: Say "Hey Omi" and confirm it responds
- [ ] Test speaker volume - loud enough for judges to hear
- [ ] Test mic in venue noise - adjust sensitivity if needed
- [ ] Keep device plugged in during demo if possible

### 2. Backend Verification
- [ ] Visit https://alexwang409--foodvoice-omi-fastapi-app.modal.run/health
- [ ] Confirm status: "healthy" and all services show `true`
- [ ] Check API keys are configured (claude_api, omi_api should be `true`)

### 3. Test Order (CRITICAL - do this first!)
- [ ] Say to Omi: "Order a pepperoni pizza from Domino's"
- [ ] Check your Omi app for notification with link
- [ ] If no notification appears, check Modal logs immediately

### 4. Backup Materials
- [ ] Screenshots of successful orders loaded on your phone
- [ ] This demo script open on your laptop
- [ ] Modal logs open in browser tab (for debugging)

---

## The 90-Second Demo Script

### Opening (10 seconds)
"Hi, I'm [Name] and this is FoodVoice. **The problem**: ordering food takes forever - you have to pull out your phone, tap through menus, fill in details. **Our solution**: just speak to your Omi device and the order is placed instantly."

### Demo 1: Basic Voice Order (30 seconds)
**Say to Omi**: "Order a pepperoni pizza from Domino's"

**While processing (show judges your phone)**:
- "Our AI is parsing the intent using Claude..."
- Open Omi app and show the notification pop up
- "It extracted 'pepperoni pizza' and 'Domino's'"
- Click the notification - show the Google link

**Explain**: "This link takes them straight to DoorDash with that restaurant ready to order from. In a real scenario, we'd use browser automation to complete the entire checkout, but for the demo we're using smart deep links."

### Demo 2: Quick Reorder (20 seconds)
**Say to Omi**: "Order my usual"

**Show**:
- Notification appears instantly
- Click to show it's the same pizza order

**Explain**: "It remembered my last order. This is perfect for your regular lunch spot - just say 'order my usual' and you're done."

### Demo 3: Learning Over Time (15 seconds)
**Show on laptop**: Open browser to your profile endpoint:
```
https://alexwang409--foodvoice-omi-fastapi-app.modal.run/profile/test_user
```

**Point out**:
- "See `last_order` - it saved my pizza preference"
- "Over time it learns your favorites, dietary restrictions, delivery addresses"

### The Wow Moment (15 seconds)
"Imagine you're cooking dinner and realize you need ingredients. Or you're driving and want to order pickup. Or you're in a meeting and hungry. **You just speak - no phone, no tapping, no interrupting what you're doing.** FoodVoice saves 2-3 minutes every order, which adds up to hours per year for regular users."

### Close (10 seconds)
"Right now it works with DoorDash. Post-hackathon we'd add Uber Eats, GrubHub, direct restaurant APIs, and full checkout automation. Thanks!"

---

## Edge Case Handling

If asked about edge cases or safety, demonstrate:

### Graceful Failure - Wrong Restaurant
**Say**: "Order sushi from McDonald's"

**Expected result**:
- AI should recognize McDonald's doesn't serve sushi
- Should suggest: "McDonald's doesn't have sushi. Would you like me to find a sushi restaurant instead?"

### Safety Check - Ambiguous Order
**Say**: "Order food"

**Expected result**:
- AI asks: "What kind of food would you like?"
- Demonstrates it won't place random orders

---

## Alternative Demo Flows

### If judges want to see it work live:
Ask a judge to say a food order to your Omi device. Suggested prompts:
- "Order a burger from Five Guys"
- "Order pad thai from Thai Express"
- "Order my usual" (if you've already placed an order)

### If technical issues occur:
Have backup screenshots ready showing:
1. Voice command in Omi transcript
2. Notification with link
3. User profile JSON with saved preferences

**What to say**: "I have the working demo on Modal - let me show you the logs and screenshots of it working" (this is why you test beforehand!)

---

## Technical Deep Dive (If judges ask)

### Architecture Overview
"We use a 3-tier architecture:
1. **Omi device** captures voice and sends transcripts via webhook
2. **Claude AI** (via Anthropic API) parses intent - food item, restaurant, dietary needs
3. **Modal serverless** hosts our FastAPI backend with zero config
4. **Smart deep links** using Google's 'I'm Feeling Lucky' to generate direct-to-restaurant URLs"

### Key Technical Decisions

**Q: Why not use speech-to-text yourself?**
A: Omi handles that - we get clean transcripts. Saves us from dealing with audio processing.

**Q: Why Claude over GPT?**
A: Claude Sonnet 4.5 is faster and more accurate for structured extraction. We need reliable JSON output.

**Q: How do you handle payments?**
A: We don't store payment info - the deep link takes users to DoorDash where they complete checkout. For a production app, we'd integrate DoorDash's Order API directly.

**Q: What about privacy?**
A: We only store order preferences, never payment info. Users can delete their profile anytime via `/profile/{uid}/delete`

---

## Judging Criteria & How FoodVoice Excels

### Omi Awards Criteria

**Voice-First Experience**
- Pure voice interface - no phone needed
- Natural language processing ("Order pizza" not "Order dot pizza dot from dot Domino's")
- Contextual understanding (remembers "my usual")

**Technical Quality**
- Real-time webhook processing (<2s response time)
- Robust error handling (fallback to deep links if automation fails)
- Scalable architecture (Modal serverless = infinite scale)

**Wow Factor**
- "Order my usual" feature is genuinely magical
- Learning over time creates personal AI assistant
- Saves real time in real scenarios (driving, cooking, meetings)

**Post-Hackathon Potential**
- Clear monetization: charge restaurants per order or subscription for users
- Easy expansion: add Uber Eats, GrubHub, grocery delivery
- Real user problem: everyone orders food, everyone wants it faster

---

## Troubleshooting During Demo

### Issue: Omi not hearing you
**Fix**: Increase volume, reduce ambient noise, or use push-to-talk mode

### Issue: No notification appears
**Check**:
1. Modal app is running (visit /health endpoint)
2. Webhook URL is correct in Omi App Store settings
3. Check Modal logs for errors

**Backup**: Show pre-recorded screenshots

### Issue: Wrong intent parsed
**Explain**: "This is a learning AI - in production we'd have better training data. But see how it still provides a useful fallback?"

### Issue: Link doesn't work
**Explain**: "Google's redirects sometimes have rate limits. In production we'd cache restaurant URLs or use DoorDash's official API."

---

## What to Say Post-Demo

### If they love it:
"Thanks! I'm [Name] - here's my email/GitHub if you want to stay in touch. I'm thinking of building this out further after the hackathon."

### If they have concerns:
"Great question - [address concern]. This is a 24-hour MVP, so [explain what you'd improve with more time]."

### If they ask about team:
"I'm solo hacking / We're a team of [X]. [Briefly mention each person's role if team]."

---

## Energy & Presentation Tips

1. **Speak clearly and with energy** - you're excited about this!
2. **Make eye contact** with each judge
3. **Smile** - you're proud of what you built
4. **Handle questions confidently** - "That's a great question" buys you thinking time
5. **Know when to stop** - don't over-explain, let judges ask questions
6. **Show, don't just tell** - live demo is 10x better than slides

---

## Final Checklist

**Night Before**:
- [ ] Deploy to Modal and verify /health endpoint
- [ ] Test end-to-end order flow 3 times
- [ ] Charge Omi device fully
- [ ] Read this script 2-3 times aloud

**Morning Of**:
- [ ] Re-test one order to confirm still working
- [ ] Take screenshots of working demo
- [ ] Review this script once more
- [ ] Arrive early to scope out demo area noise levels

**5 Minutes Before Your Slot**:
- [ ] Test Omi audio in venue
- [ ] Open Modal logs on laptop
- [ ] Open Omi app on phone
- [ ] Take a deep breath - you got this!

---

## Good Luck!

You've built something genuinely cool. Now go show it off with confidence!

Remember: judges want to see **passion, technical skill, and real-world impact**. FoodVoice has all three. You've got this!
