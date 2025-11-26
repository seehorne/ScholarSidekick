"""
Example usage script for ScholarSidekick API

This demonstrates how to:
1. Create a meeting with a transcript
2. Extract cards automatically
3. Add manual cards
4. Link cards together
5. Add updates and pings
"""

import requests
from datetime import datetime
import json

BASE_URL = "http://localhost:8000/api"

def example_workflow():
    """Example workflow demonstrating the API"""
    
    # 1. Create a meeting with transcript
    print("1. Creating meeting with transcript...")
    meeting_data = {
        "title": "Weekly 1:1 - Alice & Bob",
        "description": "Weekly check-in meeting",
        "transcript": """
        Alice: Hi Bob, let's start with the project update.
        Bob: Sure! I've completed the frontend redesign. The new dashboard is ready for review.
        Alice: That's great! We should deploy that by Friday. What about the API integration?
        Bob: I'm still working on that. I need to coordinate with the backend team.
        Alice: Okay, let's make that a priority for next week. Also, we need to discuss the Q4 roadmap.
        Bob: Right, I have some ideas about that. Should we schedule a separate meeting?
        Alice: Yes, let's do that. Can you send out the Q4 roadmap draft by Wednesday?
        Bob: Absolutely, I'll get that done.
        Alice: Perfect. One more thing - the client demo is next Tuesday. Are you prepared?
        Bob: Yes, I've been practicing. Just need to finalize the slides.
        """,
        "agenda_items": [
            "Project status update",
            "Q4 roadmap discussion",
            "Client demo preparation",
            "Team budget review"
        ],
        "meeting_date": datetime.now().isoformat(),
        "requested_card_types": ["tldr", "todo", "action_item", "question"]
    }
    
    response = requests.post(f"{BASE_URL}/meetings/", json=meeting_data)
    meeting = response.json()
    meeting_id = meeting["id"]
    print(f"✓ Meeting created (ID: {meeting_id})")
    print(f"  Generated {len(meeting['cards'])} cards")
    print(f"  Uncovered agenda items: {meeting.get('uncovered_agenda_items', [])}")
    
    # 2. Get meeting details
    print("\n2. Fetching meeting details...")
    response = requests.get(f"{BASE_URL}/meetings/{meeting_id}")
    meeting_details = response.json()
    print(f"✓ Retrieved meeting: {meeting_details['title']}")
    
    # 3. List cards for the meeting
    print("\n3. Listing cards...")
    response = requests.get(f"{BASE_URL}/cards/", params={"meeting_id": meeting_id})
    cards = response.json()
    for card in cards:
        print(f"  - [{card['card_type']}] {card['title']}")
    
    # 4. Create a manual card
    print("\n4. Creating a manual card...")
    canvas_id = meeting_details["canvases"][0]["id"] if meeting_details["canvases"] else None
    
    new_card_data = {
        "meeting_id": meeting_id,
        "canvas_id": canvas_id,
        "card_type": "todo",
        "title": "Review frontend code",
        "content": "Alice needs to review Bob's frontend redesign before Friday deployment",
        "status": "active",
        "assigned_to": "Alice",
        "position_x": 600,
        "position_y": 200,
        "tags": ["review", "frontend", "urgent"]
    }
    
    response = requests.post(f"{BASE_URL}/cards/", json=new_card_data)
    new_card = response.json()
    print(f"✓ Created card (ID: {new_card['id']}): {new_card['title']}")
    
    # 5. Create a linked card (child card)
    print("\n5. Creating a linked card...")
    linked_card_data = {
        "meeting_id": meeting_id,
        "canvas_id": canvas_id,
        "card_type": "follow_up",
        "title": "Address review comments",
        "content": "Bob to address any comments from Alice's review",
        "status": "draft",
        "parent_card_id": new_card["id"],  # Link to parent card
        "assigned_to": "Bob",
        "position_x": 650,
        "position_y": 400,
        "tags": ["follow-up", "frontend"]
    }
    
    response = requests.post(f"{BASE_URL}/cards/", json=linked_card_data)
    linked_card = response.json()
    print(f"✓ Created linked card (ID: {linked_card['id']}): {linked_card['title']}")
    print(f"  Linked to parent card ID: {linked_card['parent_card_id']}")
    
    # 6. Add an update to a card
    print("\n6. Adding update to card...")
    update_data = {
        "card_id": new_card["id"],
        "author": "Alice",
        "content": "Started reviewing the code. Looks good so far! Will finish by tomorrow.",
        "is_ping": False
    }
    
    response = requests.post(f"{BASE_URL}/cards/{new_card['id']}/updates", json=update_data)
    update = response.json()
    print(f"✓ Added update from {update['author']}")
    
    # 7. Add a ping to a card
    print("\n7. Adding ping to card...")
    ping_data = {
        "card_id": new_card["id"],
        "author": "Alice",
        "content": "@Bob Please make sure to run all tests before the final review",
        "is_ping": True,
        "pinged_user": "Bob"
    }
    
    response = requests.post(f"{BASE_URL}/cards/{new_card['id']}/updates", json=ping_data)
    ping = response.json()
    print(f"✓ Added ping from {ping['author']} to {ping['pinged_user']}")
    
    # 8. Get card with all updates
    print("\n8. Getting card details with updates...")
    response = requests.get(f"{BASE_URL}/cards/{new_card['id']}")
    card_detail = response.json()
    print(f"✓ Card: {card_detail['title']}")
    print(f"  Status: {card_detail['status']}")
    print(f"  Updates: {len(card_detail['updates'])}")
    for upd in card_detail['updates']:
        prefix = "📌 PING" if upd['is_ping'] else "💬"
        print(f"    {prefix} {upd['author']}: {upd['content'][:50]}...")
    
    # 9. Update card positions (batch update)
    print("\n9. Updating card positions on canvas...")
    position_updates = [
        {"id": cards[0]["id"], "position_x": 100, "position_y": 100},
        {"id": cards[1]["id"], "position_x": 400, "position_y": 100},
        {"id": new_card["id"], "position_x": 700, "position_y": 100},
    ]
    
    response = requests.post(f"{BASE_URL}/cards/batch-update-positions", json=position_updates)
    updated = response.json()
    print(f"✓ Updated positions for {len(updated)} cards")
    
    # 10. Get canvas with all cards
    print("\n10. Getting canvas view...")
    if canvas_id:
        response = requests.get(f"{BASE_URL}/canvas/{canvas_id}")
        canvas = response.json()
        print(f"✓ Canvas: {canvas['title']}")
        print(f"  Total cards: {len(canvas['cards'])}")
        print(f"  Card layout:")
        for card in canvas['cards']:
            print(f"    - {card['title']} at ({card['position_x']}, {card['position_y']})")
    
    print("\n" + "="*60)
    print("Example workflow completed successfully!")
    print("="*60)
    print(f"\nView the API docs at: http://localhost:8000/docs")
    print(f"Meeting ID: {meeting_id}")
    print(f"Canvas ID: {canvas_id}")

if __name__ == "__main__":
    try:
        example_workflow()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API")
        print("Make sure the server is running: python run.py")
    except Exception as e:
        print(f"❌ Error: {e}")
