#!/usr/bin/env python3
"""
Live Server Test - Tests the Flask server with actual HTTP requests
Run this after starting the Flask server with: python run.py
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5001"

def test_live_server():
    print("\n" + "="*70)
    print("🌐 LIVE SERVER TEST - ScholarSidekick API")
    print("="*70 + "\n")
    
    try:
        # Test 1: Health Check
        print("✓ Test 1: Health Endpoint")
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        print(f"  ✅ {response.json()}")
        
        # Test 2: Root Endpoint
        print("\n✓ Test 2: Root Endpoint")
        response = requests.get(f"{BASE_URL}/", timeout=5)
        assert response.status_code == 200
        print(f"  ✅ {response.json()}")
        
        # Test 3: Create Meeting
        print("\n✓ Test 3: Create Meeting")
        meeting_data = {
            "title": "Live Test Meeting",
            "description": "Testing with HTTP requests",
            "transcript": "This is a test transcript for validating the live server. We need to discuss the API implementation and testing strategy.",
            "meeting_date": datetime.utcnow().isoformat(),
            "agenda_items": ["API Testing", "Server Validation"],
            "requested_card_types": ["tldr", "todo", "action_item"]
        }
        response = requests.post(
            f"{BASE_URL}/api/meetings/",
            json=meeting_data,
            timeout=5
        )
        assert response.status_code == 200
        meeting = response.json()
        meeting_id = meeting['id']
        print(f"  ✅ Created meeting ID: {meeting_id}")
        print(f"     - Cards generated: {len(meeting['cards'])}")
        
        # Test 4: Get Meetings
        print("\n✓ Test 4: List Meetings")
        response = requests.get(f"{BASE_URL}/api/meetings/", timeout=5)
        assert response.status_code == 200
        meetings = response.json()
        print(f"  ✅ Found {len(meetings)} meeting(s)")
        
        # Test 5: Create a Manual Card
        print("\n✓ Test 5: Create Manual Card")
        card_data = {
            "meeting_id": meeting_id,
            "card_type": "todo",
            "title": "Live Server Test Card",
            "content": "This card was created via HTTP request"
        }
        response = requests.post(
            f"{BASE_URL}/api/cards/",
            json=card_data,
            timeout=5
        )
        assert response.status_code == 200
        card = response.json()
        card_id = card['id']
        print(f"  ✅ Created card ID: {card_id}")
        
        # Test 6: Update Card
        print("\n✓ Test 6: Update Card")
        update_data = {
            "status": "completed",
            "content": "Updated via HTTP request"
        }
        response = requests.put(
            f"{BASE_URL}/api/cards/{card_id}",
            json=update_data,
            timeout=5
        )
        assert response.status_code == 200
        updated_card = response.json()
        assert updated_card['status'] == 'completed'
        print(f"  ✅ Card status: {updated_card['status']}")
        
        print("\n" + "="*70)
        print("🎉 ALL LIVE SERVER TESTS PASSED!")
        print("="*70)
        print(f"\n✅ Server is running correctly at {BASE_URL}")
        print("✅ All endpoints responding as expected")
        print("✅ Database operations working")
        print("\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server")
        print(f"   Make sure the Flask server is running at {BASE_URL}")
        print("   Start it with: python run.py")
        print()
        return False
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_live_server()
    exit(0 if success else 1)
