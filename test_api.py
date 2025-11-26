#!/usr/bin/env python3
"""
Test script for ScholarSidekick Flask API
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5001"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_root():
    """Test root endpoint"""
    print("\n🔍 Testing Root Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_create_meeting():
    """Test creating a meeting"""
    print("\n🔍 Testing Create Meeting...")
    meeting_data = {
        "title": "Test Weekly 1:1 - Alice & Bob",
        "description": "Testing the Flask API",
        "transcript": """
        Alice: Hi Bob, how's the project going?
        Bob: Great! I've completed the frontend redesign.
        Alice: Excellent! We should deploy that by Friday.
        Bob: Sounds good. I also need to work on the API integration.
        Alice: Let's make that a priority for next week.
        """,
        "agenda_items": [
            "Project status update",
            "Deployment planning",
            "API integration"
        ],
        "meeting_date": datetime.now().isoformat(),
        "requested_card_types": ["tldr", "todo", "action_item"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/meetings/", json=meeting_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            meeting = response.json()
            print(f"   ✅ Created meeting ID: {meeting['id']}")
            print(f"   Title: {meeting['title']}")
            print(f"   Cards generated: {len(meeting.get('cards', []))}")
            print(f"   Canvases created: {len(meeting.get('canvases', []))}")
            if meeting.get('uncovered_agenda_items'):
                print(f"   Uncovered items: {meeting['uncovered_agenda_items']}")
            return meeting
        else:
            print(f"   ❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_list_meetings():
    """Test listing meetings"""
    print("\n🔍 Testing List Meetings...")
    try:
        response = requests.get(f"{BASE_URL}/api/meetings/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            meetings = response.json()
            print(f"   ✅ Found {len(meetings)} meeting(s)")
            for m in meetings:
                print(f"      - {m['title']} (ID: {m['id']})")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_get_meeting(meeting_id):
    """Test getting a specific meeting"""
    print(f"\n🔍 Testing Get Meeting {meeting_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/meetings/{meeting_id}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            meeting = response.json()
            print(f"   ✅ Meeting: {meeting['title']}")
            print(f"   Cards: {len(meeting.get('cards', []))}")
            print(f"   Canvases: {len(meeting.get('canvases', []))}")
            return meeting
        else:
            print(f"   ❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_create_card(meeting_id, canvas_id):
    """Test creating a manual card"""
    print(f"\n🔍 Testing Create Card...")
    card_data = {
        "meeting_id": meeting_id,
        "canvas_id": canvas_id,
        "card_type": "todo",
        "title": "Review test results",
        "content": "Alice needs to review the API test results",
        "status": "active",
        "assigned_to": "Alice",
        "position_x": 100,
        "position_y": 200,
        "tags": ["testing", "review"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/cards/", json=card_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            card = response.json()
            print(f"   ✅ Created card ID: {card['id']}")
            print(f"   Title: {card['title']}")
            print(f"   Type: {card['card_type']}")
            return card
        else:
            print(f"   ❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_add_card_update(card_id):
    """Test adding an update to a card"""
    print(f"\n🔍 Testing Add Card Update...")
    update_data = {
        "card_id": card_id,
        "author": "Bob",
        "content": "I've started working on this task!",
        "is_ping": True,
        "pinged_user": "Alice"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/cards/{card_id}/updates", json=update_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            update = response.json()
            print(f"   ✅ Created update ID: {update['id']}")
            print(f"   Author: {update['author']}")
            print(f"   Ping: {update['is_ping']}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_list_cards(meeting_id):
    """Test listing cards"""
    print(f"\n🔍 Testing List Cards for Meeting {meeting_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/cards/", params={"meeting_id": meeting_id})
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            cards = response.json()
            print(f"   ✅ Found {len(cards)} card(s)")
            for c in cards:
                print(f"      - [{c['card_type']}] {c['title']}")
            return cards
        else:
            print(f"   ❌ Error: {response.text}")
            return []
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 ScholarSidekick Flask API Tests")
    print("=" * 60)
    
    # Test basic endpoints
    if not test_health():
        print("\n❌ Server is not running! Please start it with: python run.py")
        return
    
    test_root()
    
    # Test meeting endpoints
    meeting = test_create_meeting()
    if not meeting:
        print("\n❌ Failed to create meeting, stopping tests")
        return
    
    meeting_id = meeting['id']
    canvas_id = meeting['canvases'][0]['id'] if meeting.get('canvases') else None
    
    test_list_meetings()
    meeting_detail = test_get_meeting(meeting_id)
    
    # Test card endpoints
    if canvas_id:
        card = test_create_card(meeting_id, canvas_id)
        if card:
            test_add_card_update(card['id'])
    
    test_list_cards(meeting_id)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   Meeting ID: {meeting_id}")
    print(f"   Canvas ID: {canvas_id}")
    print(f"   API Base URL: {BASE_URL}")
    print(f"\n💡 You can now:")
    print(f"   - View meeting: {BASE_URL}/api/meetings/{meeting_id}")
    print(f"   - View canvas: {BASE_URL}/api/canvas/{canvas_id}")
    print(f"   - List all cards: {BASE_URL}/api/cards/?meeting_id={meeting_id}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
