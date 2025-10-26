#!/bin/bash
# Quick local testing script

echo "🧪 Testing FoodVoice API locally..."
echo ""

# Check if server is running
echo "1️⃣ Health check..."
curl -s http://localhost:8000/health | jq .
echo ""

echo "2️⃣ Testing food order intent..."
curl -s -X POST http://localhost:8000/webhook/transcript \
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
  }' | jq .
echo ""

echo "3️⃣ Checking user profile..."
curl -s http://localhost:8000/profile/test_user | jq .
echo ""

echo "4️⃣ Testing quick reorder..."
curl -s -X POST http://localhost:8000/webhook/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test123",
    "segments": [
      {
        "text": "Order my usual",
        "speaker": "User",
        "speaker_id": 0,
        "is_user": true,
        "start": 0.0,
        "end": 1.5
      }
    ]
  }' | jq .
echo ""

echo "✅ Tests complete!"
