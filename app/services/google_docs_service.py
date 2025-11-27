"""
Google Docs Integration Service

Handles OAuth2 authentication and fetching documents from Google Docs.
"""

import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleDocsService:
    """Service for integrating with Google Docs API"""
    
    # OAuth2 scopes needed for Google Docs
    SCOPES = [
        'https://www.googleapis.com/auth/documents.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    def __init__(self):
        """Initialize the Google Docs service"""
        self.client_config = self._load_client_config()
        
    def _load_client_config(self):
        """Load OAuth2 client configuration from environment or file"""
        # Try to load from environment variable first
        config_json = os.getenv('GOOGLE_CLIENT_CONFIG')
        if config_json:
            return json.loads(config_json)
        
        # Try to load from file
        config_file = os.getenv('GOOGLE_CLIENT_SECRETS_FILE', 'client_secrets.json')
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        
        # Return None if no config found
        return None
    
    def create_authorization_url(self, redirect_uri):
        """
        Create an authorization URL for OAuth2 flow
        
        Args:
            redirect_uri: The URI to redirect to after authorization
            
        Returns:
            tuple: (authorization_url, state)
        """
        if not self.client_config:
            raise ValueError("Google OAuth2 client configuration not found")
        
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return authorization_url, state
    
    def exchange_code_for_token(self, code, redirect_uri, state):
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from OAuth2 callback
            redirect_uri: The redirect URI used in authorization
            state: The state parameter from authorization
            
        Returns:
            dict: Token information
        """
        if not self.client_config:
            raise ValueError("Google OAuth2 client configuration not found")
        
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri,
            state=state
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
    
    def get_document_content(self, document_id, token_info):
        """
        Fetch content from a Google Doc
        
        Args:
            document_id: The ID of the Google Doc
            token_info: Token information dict
            
        Returns:
            str: The text content of the document
        """
        try:
            # Create credentials from token info
            credentials = Credentials(
                token=token_info['token'],
                refresh_token=token_info.get('refresh_token'),
                token_uri=token_info.get('token_uri'),
                client_id=token_info.get('client_id'),
                client_secret=token_info.get('client_secret'),
                scopes=token_info.get('scopes')
            )
            
            # Build the Docs API service
            service = build('docs', 'v1', credentials=credentials)
            
            # Fetch the document
            document = service.documents().get(documentId=document_id).execute()
            
            # Extract text content
            content = self._extract_text_from_document(document)
            
            return content
            
        except HttpError as error:
            raise Exception(f"Failed to fetch Google Doc: {error}")
    
    def _extract_text_from_document(self, document):
        """
        Extract plain text from Google Docs API response
        
        Args:
            document: The document object from Google Docs API
            
        Returns:
            str: Extracted plain text
        """
        text_parts = []
        
        if 'body' not in document or 'content' not in document['body']:
            return ""
        
        for element in document['body']['content']:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                if 'elements' in paragraph:
                    for elem in paragraph['elements']:
                        if 'textRun' in elem:
                            text_parts.append(elem['textRun']['content'])
            elif 'table' in element:
                # Handle tables
                table = element['table']
                for row in table.get('tableRows', []):
                    for cell in row.get('tableCells', []):
                        for content_elem in cell.get('content', []):
                            if 'paragraph' in content_elem:
                                paragraph = content_elem['paragraph']
                                if 'elements' in paragraph:
                                    for elem in paragraph['elements']:
                                        if 'textRun' in elem:
                                            text_parts.append(elem['textRun']['content'])
        
        return ''.join(text_parts)
    
    def extract_document_id_from_url(self, url):
        """
        Extract document ID from Google Docs URL
        
        Args:
            url: Google Docs URL
            
        Returns:
            str: Document ID or None
        """
        import re
        
        # Pattern for Google Docs URLs
        patterns = [
            r'/document/d/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_document_metadata(self, document_id, token_info):
        """
        Get metadata about a Google Doc
        
        Args:
            document_id: The ID of the Google Doc
            token_info: Token information dict
            
        Returns:
            dict: Document metadata (title, etc.)
        """
        try:
            credentials = Credentials(
                token=token_info['token'],
                refresh_token=token_info.get('refresh_token'),
                token_uri=token_info.get('token_uri'),
                client_id=token_info.get('client_id'),
                client_secret=token_info.get('client_secret'),
                scopes=token_info.get('scopes')
            )
            
            service = build('docs', 'v1', credentials=credentials)
            document = service.documents().get(documentId=document_id).execute()
            
            return {
                'title': document.get('title', 'Untitled'),
                'document_id': document_id,
                'revision_id': document.get('revisionId')
            }
            
        except HttpError as error:
            raise Exception(f"Failed to fetch document metadata: {error}")
