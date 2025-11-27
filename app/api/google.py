"""
Google API endpoints for OAuth and document fetching
"""

from flask import Blueprint, request, jsonify, session, redirect
from app.services.google_docs_service import GoogleDocsService
import os

bp = Blueprint('google', __name__, url_prefix='/api/google')

google_service = GoogleDocsService()

@bp.route('/auth/url', methods=['GET'])
def get_auth_url():
    """
    Get Google OAuth2 authorization URL
    
    Returns the URL to redirect users to for Google authentication
    """
    try:
        # Get the redirect URI from request or use default
        redirect_uri = request.args.get(
            'redirect_uri',
            f"{request.host_url}api/google/auth/callback"
        )
        
        auth_url, state = google_service.create_authorization_url(redirect_uri)
        
        # Store state in session for CSRF protection
        session['google_auth_state'] = state
        
        return jsonify({
            'authorization_url': auth_url,
            'state': state
        })
        
    except ValueError as e:
        return jsonify({
            'error': str(e),
            'message': 'Google OAuth configuration not found. Please set up client credentials.'
        }), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/auth/callback', methods=['GET'])
def auth_callback():
    """
    OAuth2 callback endpoint
    
    Exchanges authorization code for access token
    """
    try:
        # Get authorization code and state from query params
        code = request.args.get('code')
        state = request.args.get('state')
        
        if not code:
            return jsonify({'error': 'No authorization code provided'}), 400
        
        # Verify state for CSRF protection
        stored_state = session.get('google_auth_state')
        if state != stored_state:
            return jsonify({'error': 'Invalid state parameter'}), 400
        
        # Get redirect URI
        redirect_uri = f"{request.host_url}api/google/auth/callback"
        
        # Exchange code for token
        token_info = google_service.exchange_code_for_token(code, redirect_uri, state)
        
        # Store token in session (in production, store in database)
        session['google_token'] = token_info
        
        return jsonify({
            'message': 'Successfully authenticated with Google',
            'token_received': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/document/<document_id>', methods=['GET'])
def get_document(document_id):
    """
    Fetch content from a Google Doc
    
    Args:
        document_id: The ID of the Google Doc
        
    Query Parameters:
        token: Optional - Google access token (if not in session)
    """
    try:
        # Get token from session or query parameter
        token_info = session.get('google_token')
        
        # Allow passing token in request for API use
        if not token_info:
            token = request.args.get('token')
            if token:
                token_info = {'token': token}
        
        if not token_info:
            return jsonify({
                'error': 'Not authenticated',
                'message': 'Please authenticate with Google first'
            }), 401
        
        # Fetch document content
        content = google_service.get_document_content(document_id, token_info)
        metadata = google_service.get_document_metadata(document_id, token_info)
        
        return jsonify({
            'document_id': document_id,
            'title': metadata['title'],
            'content': content,
            'metadata': metadata
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/document/from-url', methods=['POST'])
def get_document_from_url():
    """
    Fetch content from a Google Doc using its URL
    
    Request body:
        {
            "url": "https://docs.google.com/document/d/...",
            "token": "optional_access_token"
        }
    """
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Extract document ID from URL
        document_id = google_service.extract_document_id_from_url(url)
        
        if not document_id:
            return jsonify({'error': 'Invalid Google Docs URL'}), 400
        
        # Get token from request or session
        token_info = data.get('token_info') or session.get('google_token')
        
        if not token_info:
            return jsonify({
                'error': 'Not authenticated',
                'message': 'Please authenticate with Google first'
            }), 401
        
        # Fetch document content
        content = google_service.get_document_content(document_id, token_info)
        metadata = google_service.get_document_metadata(document_id, token_info)
        
        return jsonify({
            'document_id': document_id,
            'title': metadata['title'],
            'content': content,
            'metadata': metadata
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/auth/status', methods=['GET'])
def auth_status():
    """Check if user is authenticated with Google"""
    token_info = session.get('google_token')
    
    return jsonify({
        'authenticated': token_info is not None,
        'has_token': token_info is not None
    })

@bp.route('/auth/logout', methods=['POST'])
def logout():
    """Log out from Google (clear session)"""
    session.pop('google_token', None)
    session.pop('google_auth_state', None)
    
    return jsonify({
        'message': 'Successfully logged out from Google'
    })
