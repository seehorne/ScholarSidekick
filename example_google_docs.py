"""
Example: Using Google Docs Integration

This example demonstrates how to:
1. Authenticate with Google
2. Fetch a document from Google Docs
3. Create a meeting with the document content
"""

import requests
import webbrowser
import time

BASE_URL = "http://localhost:5001"

def main():
    print("=" * 60)
    print("ScholarSidekick - Google Docs Integration Example")
    print("=" * 60)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Get Google authorization URL
    print("\n1. Getting Google authorization URL...")
    try:
        response = session.get(f"{BASE_URL}/api/google/auth/url")
        response.raise_for_status()
        auth_data = response.json()
        
        print(f"\n✅ Authorization URL received")
        print(f"\nPlease visit this URL to authorize:")
        print(f"\n{auth_data['authorization_url']}\n")
        
        # Optionally open in browser
        open_browser = input("Open in browser? (y/n): ")
        if open_browser.lower() == 'y':
            webbrowser.open(auth_data['authorization_url'])
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error getting authorization URL: {e}")
        print("\nMake sure:")
        print("1. The server is running (python run.py)")
        print("2. Google OAuth is configured (see GOOGLE_SETUP.md)")
        return
    
    # Step 2: Wait for user to complete OAuth flow
    print("\nAfter authorizing, the callback will automatically handle the token.")
    input("\nPress Enter after you've completed the authorization...")
    
    # Step 3: Check authentication status
    print("\n2. Checking authentication status...")
    response = session.get(f"{BASE_URL}/api/google/auth/status")
    auth_status = response.json()
    
    if not auth_status.get('authenticated'):
        print("❌ Not authenticated. Please complete the OAuth flow first.")
        return
    
    print("✅ Authenticated with Google!")
    
    # Step 4: Get Google Docs URL from user
    print("\n3. Enter your Google Docs URL:")
    print("Example: https://docs.google.com/document/d/ABC123.../edit")
    doc_url = input("\nGoogle Docs URL: ").strip()
    
    if not doc_url:
        print("❌ No URL provided")
        return
    
    # Step 5: Create meeting with Google Doc
    print("\n4. Creating meeting from Google Doc...")
    
    meeting_data = {
        "google_doc_url": doc_url,
        "meeting_date": "2025-11-27T10:00:00",
        "agenda_items": ["Discussion points", "Action items"],
        "requested_card_types": ["tldr", "todo", "action_item"]
    }
    
    try:
        response = session.post(
            f"{BASE_URL}/api/meetings/",
            json=meeting_data
        )
        response.raise_for_status()
        meeting = response.json()
        
        print("\n✅ Meeting created successfully!")
        print(f"\nMeeting ID: {meeting['id']}")
        print(f"Title: {meeting['title']}")
        print(f"Transcript length: {len(meeting['transcript'])} characters")
        print(f"Cards generated: {len(meeting.get('cards', []))}")
        
        if meeting.get('cards'):
            print("\nGenerated cards:")
            for card in meeting['cards']:
                print(f"  - [{card['card_type']}] {card['title']}")
        
        print(f"\nFirst 200 characters of transcript:")
        print(meeting['transcript'][:200] + "...")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error creating meeting: {e}")
        if hasattr(e.response, 'json'):
            print(f"Details: {e.response.json()}")
        return
    
    # Step 6: Demonstrate fetching doc directly
    print("\n5. Fetching document directly...")
    
    response = session.post(
        f"{BASE_URL}/api/google/document/from-url",
        json={"url": doc_url}
    )
    
    if response.status_code == 200:
        doc_data = response.json()
        print(f"\n✅ Document fetched:")
        print(f"Title: {doc_data['title']}")
        print(f"Content length: {len(doc_data['content'])} characters")
    else:
        print(f"❌ Error: {response.json()}")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)

if __name__ == "__main__":
    print("\nMake sure the server is running: python run.py\n")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
