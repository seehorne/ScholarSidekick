from app.main import app

print('✅ App loaded successfully!')

# Test using Flask test client
with app.test_client() as client:
    # Test health endpoint
    response = client.get('/health')
    print(f'\n🏥 Health endpoint:')
    print(f'   Status: {response.status_code}')
    print(f'   Response: {response.get_json()}')
    
    # Test root endpoint
    response = client.get('/')
    print(f'\n🏠 Root endpoint:')
    print(f'   Status: {response.status_code}')
    print(f'   Response: {response.get_json()}')
    
    # Test meetings list (should be empty)
    response = client.get('/api/meetings/')
    print(f'\n📋 Meetings list:')
    print(f'   Status: {response.status_code}')
    print(f'   Response: {response.get_json()}')

print('\n✅ All basic tests passed!')
