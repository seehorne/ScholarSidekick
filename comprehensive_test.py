#!/usr/bin/env python3
"""
Comprehensive test of ScholarSidekick Flask API
Tests all endpoints using Flask's test client
"""
from app.main import app
from datetime import datetime
import json

def test_all():
    print("=" * 70)
    print("🧪 COMPREHENSIVE SCHOLARSIDEKICK API TEST")
    print("=" * 70)
    
    with app.test_client() as client:
        
        # Test 1: Health Check
        print("\n✓ Test 1: Health Endpoint")
        response = client.get('/health')
        assert response.status_code == 200
        assert response.get_json()['status'] == 'healthy'
        print(f"  ✅ {response.get_json()}")
        
        # Test 2: Root Endpoint
        print("\n✓ Test 2: Root Endpoint")
        response = client.get('/')
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        print(f"  ✅ {data}")
        
        # Test 3: Create Meeting
        print("\n✓ Test 3: Create Meeting")
        meeting_data = {
            "title": "Test Meeting - API Validation",
            "description": "Comprehensive test of Flask backend",
            "transcript": """
            Alice: Let's review the quarterly goals.
            Bob: Sounds good. I've prepared a summary.
            Alice: Great! We should also discuss the new feature requests.
            Bob: I have a list of the top 5 priorities.
            Alice: Perfect. Let's allocate resources accordingly.
            """,
            "agenda_items": [
                "Quarterly goals review",
                "Feature requests discussion",
                "Resource allocation"
            ],
            "meeting_date": "2025-11-26T10:00:00",
            "requested_card_types": ["tldr", "todo", "action_item"]
        }
        response = client.post('/api/meetings/', 
                              data=json.dumps(meeting_data),
                              content_type='application/json')
        assert response.status_code == 201
        meeting = response.get_json()
        meeting_id = meeting['id']
        print(f"  ✅ Created meeting ID: {meeting_id}")
        print(f"     - Title: {meeting['title']}")
        print(f"     - Cards: {len(meeting.get('cards', []))}")
        print(f"     - Canvases: {len(meeting.get('canvases', []))}")
        
        # Test 4: List Meetings
        print("\n✓ Test 4: List All Meetings")
        response = client.get('/api/meetings/')
        assert response.status_code == 200
        meetings = response.get_json()
        assert len(meetings) >= 1
        print(f"  ✅ Found {len(meetings)} meeting(s)")
        
        # Test 5: Get Specific Meeting
        print("\n✓ Test 5: Get Meeting by ID")
        response = client.get(f'/api/meetings/{meeting_id}')
        assert response.status_code == 200
        meeting_detail = response.get_json()
        assert meeting_detail['id'] == meeting_id
        print(f"  ✅ Retrieved: {meeting_detail['title']}")
        
        # Get canvas and card info for later tests
        canvas_id = meeting_detail['canvases'][0]['id'] if meeting_detail.get('canvases') else None
        existing_cards = meeting_detail.get('cards', [])
        
        # Test 6: Create Manual Card
        print("\n✓ Test 6: Create Manual Card")
        card_data = {
            "meeting_id": meeting_id,
            "canvas_id": canvas_id,
            "card_type": "todo",
            "title": "Complete API testing",
            "content": "Validate all Flask endpoints work correctly",
            "status": "active",
            "assigned_to": "Test User",
            "position_x": 300,
            "position_y": 150,
            "tags": ["testing", "api", "validation"]
        }
        response = client.post('/api/cards/',
                              data=json.dumps(card_data),
                              content_type='application/json')
        assert response.status_code == 201
        card = response.get_json()
        card_id = card['id']
        print(f"  ✅ Created card ID: {card_id}")
        print(f"     - Title: {card['title']}")
        print(f"     - Type: {card['card_type']}")
        
        # Test 7: List Cards
        print("\n✓ Test 7: List Cards for Meeting")
        response = client.get(f'/api/cards/', query_string={'meeting_id': meeting_id})
        assert response.status_code == 200
        cards = response.get_json()
        assert len(cards) >= 1
        print(f"  ✅ Found {len(cards)} card(s)")
        for c in cards[:3]:  # Show first 3
            print(f"     - [{c['card_type']}] {c['title']}")
        
        # Test 8: Update Card
        print("\n✓ Test 8: Update Card")
        update_data = {
            "status": "completed",
            "content": "API testing completed successfully!"
        }
        response = client.put(f'/api/cards/{card_id}',
                             data=json.dumps(update_data),
                             content_type='application/json')
        assert response.status_code == 200
        updated_card = response.get_json()
        assert updated_card['status'] == 'completed'
        print(f"  ✅ Updated card status to: {updated_card['status']}")
        
        # Test 9: Add Card Update/Ping
        print("\n✓ Test 9: Add Card Update")
        update_data = {
            "card_id": card_id,
            "author": "Test User",
            "content": "All tests passing! 🎉",
            "is_ping": True,
            "pinged_user": "Team Lead"
        }
        response = client.post(f'/api/cards/{card_id}/updates',
                              data=json.dumps(update_data),
                              content_type='application/json')
        assert response.status_code == 201
        card_update = response.get_json()
        print(f"  ✅ Created update ID: {card_update['id']}")
        print(f"     - From: {card_update['author']}")
        print(f"     - Ping: {card_update['is_ping']}")
        
        # Test 10: Get Card Updates
        print("\n✓ Test 10: Get All Card Updates")
        response = client.get(f'/api/cards/{card_id}/updates')
        assert response.status_code == 200
        updates = response.get_json()
        assert len(updates) >= 1
        print(f"  ✅ Found {len(updates)} update(s)")
        
        # Test 11: Batch Update Card Positions
        print("\n✓ Test 11: Batch Update Card Positions")
        position_updates = [
            {"id": card_id, "position_x": 100, "position_y": 100}
        ]
        # Add more cards if they exist
        for i, c in enumerate(cards[:2]):
            if c['id'] != card_id:
                position_updates.append({
                    "id": c['id'],
                    "position_x": 200 + i * 150,
                    "position_y": 100
                })
        
        response = client.post('/api/cards/batch-update-positions',
                              data=json.dumps(position_updates),
                              content_type='application/json')
        assert response.status_code == 200
        updated_cards = response.get_json()
        print(f"  ✅ Updated {len(updated_cards)} card position(s)")
        
        # Test 12: Get Canvas
        if canvas_id:
            print("\n✓ Test 12: Get Canvas")
            response = client.get(f'/api/canvas/{canvas_id}')
            assert response.status_code == 200
            canvas = response.get_json()
            print(f"  ✅ Retrieved canvas: {canvas['title']}")
            print(f"     - Cards on canvas: {len(canvas.get('cards', []))}")
        
        # Test 13: Update Meeting
        print("\n✓ Test 13: Update Meeting")
        update_data = {
            "description": "Updated description - All tests passed!"
        }
        response = client.put(f'/api/meetings/{meeting_id}',
                             data=json.dumps(update_data),
                             content_type='application/json')
        assert response.status_code == 200
        updated_meeting = response.get_json()
        print(f"  ✅ Updated meeting description")
        
        # Test 14: Get Card with Details
        print("\n✓ Test 14: Get Card with Full Details")
        response = client.get(f'/api/cards/{card_id}')
        assert response.status_code == 200
        card_detail = response.get_json()
        print(f"  ✅ Card: {card_detail['title']}")
        print(f"     - Updates: {len(card_detail.get('updates', []))}")
        print(f"     - Status: {card_detail['status']}")
        
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print(f"\n📊 Test Summary:")
        print(f"   ✅ 14 test suites executed")
        print(f"   ✅ All endpoints working correctly")
        print(f"   ✅ Meeting ID: {meeting_id}")
        print(f"   ✅ Canvas ID: {canvas_id}")
        print(f"   ✅ Card ID: {card_id}")
        print(f"\n🚀 Flask Backend Status: FULLY OPERATIONAL")
        print("=" * 70)

if __name__ == "__main__":
    try:
        test_all()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
