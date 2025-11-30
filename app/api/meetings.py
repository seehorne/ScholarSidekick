import os
import logging
from flask import Blueprint, request, jsonify, session
from datetime import datetime
from app.database import db
from app.models import Meeting, Card, Canvas, CardType
from app.schemas import MeetingSchema, MeetingCreateSchema, MeetingDetailSchema
from app.services.extraction_service import ExtractionService
from app.services.google_docs_service import GoogleDocsService

logger = logging.getLogger(__name__)

bp = Blueprint('meetings', __name__)

meeting_schema = MeetingSchema()
meetings_schema = MeetingSchema(many=True)
meeting_create_schema = MeetingCreateSchema()
meeting_detail_schema = MeetingDetailSchema()
google_service = GoogleDocsService()


def get_extraction_service() -> ExtractionService:
    """Get ExtractionService instance with API key from environment."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    return ExtractionService(api_key=api_key)

@bp.route('/', methods=['POST'])
def create_meeting():
    """
    Create a new meeting and extract cards from transcript.
    
    This endpoint supports:
    1. Direct transcript text
    2. Google Docs URL (requires authentication)
    
    Request body can include:
    - transcript: Direct text
    - google_doc_url: URL to Google Doc
    - google_doc_id: Direct document ID
    
    This endpoint:
    1. Fetches transcript (from text or Google Doc)
    2. Creates a meeting record
    3. Extracts cards based on requested_card_types (placeholder for LLM)
    4. Creates a default canvas
    5. Returns meeting with generated cards
    """
    data = request.get_json()
    
    # Handle Google Docs integration
    transcript = data.get('transcript')
    google_doc_url = data.get('google_doc_url')
    google_doc_id = data.get('google_doc_id')
    
    if not transcript and not google_doc_url and not google_doc_id:
        return jsonify({
            'error': 'Either transcript, google_doc_url, or google_doc_id is required'
        }), 400
    
    # Fetch from Google Docs if URL or ID provided
    if google_doc_url or google_doc_id:
        try:
            # Get token from session or request
            token_info = data.get('token_info') or session.get('google_token')
            
            if not token_info:
                return jsonify({
                    'error': 'Google authentication required',
                    'message': 'Please authenticate with Google first using /api/google/auth/url'
                }), 401
            
            # Extract document ID if URL provided
            if google_doc_url:
                google_doc_id = google_service.extract_document_id_from_url(google_doc_url)
                if not google_doc_id:
                    return jsonify({'error': 'Invalid Google Docs URL'}), 400
            
            # Fetch document content
            transcript = google_service.get_document_content(google_doc_id, token_info)
            doc_metadata = google_service.get_document_metadata(google_doc_id, token_info)
            
            # Use document title if no title provided
            if not data.get('title'):
                data['title'] = doc_metadata['title']
            
        except Exception as e:
            return jsonify({
                'error': 'Failed to fetch Google Doc',
                'message': str(e)
            }), 500
    
    # Update data with fetched transcript
    data['transcript'] = transcript
    
    errors = meeting_create_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    
    # Parse datetime if it's a string
    if isinstance(data.get('meeting_date'), str):
        data['meeting_date'] = datetime.fromisoformat(data['meeting_date'].replace('Z', '+00:00'))
    
    # Create meeting
    meeting = Meeting(
        title=data['title'],
        description=data.get('description'),
        transcript=data['transcript'],
        agenda_items=data.get('agenda_items'),
        meeting_date=data['meeting_date']
    )
    db.session.add(meeting)
    db.session.flush()  # Get the meeting ID
    
    # Create default canvas for this meeting
    canvas = Canvas(
        meeting_id=meeting.id,
        title=f"{data['title']} - Canvas",
        description="Main canvas for meeting cards"
    )
    db.session.add(canvas)
    db.session.flush()
    
    # Extract cards from transcript using Gemini LLM
    try:
        extraction_service = get_extraction_service()
    except ValueError as e:
        logger.error(f"Failed to initialize extraction service: {e}")
        return jsonify({
            'error': 'LLM service not configured',
            'message': str(e)
        }), 500
    
    requested_types = [CardType(t) for t in data.get('requested_card_types', [CardType.TLDR.value, CardType.TODO.value])]
    extracted_cards = extraction_service.extract_cards(
        transcript=data['transcript'],
        agenda_items=data.get('agenda_items'),
        requested_types=requested_types
    )
    
    # Create card records
    for card_data in extracted_cards:
        card = Card(
            meeting_id=meeting.id,
            canvas_id=canvas.id,
            card_type=card_data["type"],
            title=card_data["title"],
            content=card_data["content"],
            is_generated=True,
            transcript_segment=card_data.get("segment"),
            position_x=card_data.get("position_x", 0),
            position_y=card_data.get("position_y", 0)
        )
        db.session.add(card)
    
    # Check for uncovered agenda items (placeholder)
    if data.get('agenda_items'):
        uncovered = extraction_service.find_uncovered_agenda_items(
            agenda_items=data['agenda_items'],
            transcript=data['transcript']
        )
        meeting.uncovered_agenda_items = uncovered
    
    db.session.commit()
    
    return jsonify(meeting_detail_schema.dump(meeting)), 201

@bp.route('/', methods=['GET'])
def list_meetings():
    """List all meetings"""
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    
    meetings = Meeting.query.offset(skip).limit(limit).all()
    return jsonify(meetings_schema.dump(meetings))

@bp.route('/<int:meeting_id>', methods=['GET'])
def get_meeting(meeting_id):
    """Get a specific meeting with all cards and canvases"""
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404
    
    return jsonify(meeting_detail_schema.dump(meeting))

@bp.route('/<int:meeting_id>', methods=['PUT'])
def update_meeting(meeting_id):
    """Update a meeting"""
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404
    
    data = request.get_json()
    
    # Parse datetime if it's a string
    if 'meeting_date' in data and isinstance(data['meeting_date'], str):
        data['meeting_date'] = datetime.fromisoformat(data['meeting_date'].replace('Z', '+00:00'))
    
    for field in ['title', 'description', 'transcript', 'agenda_items', 'meeting_date']:
        if field in data:
            setattr(meeting, field, data[field])
    
    meeting.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(meeting_schema.dump(meeting))

@bp.route('/<int:meeting_id>', methods=['DELETE'])
def delete_meeting(meeting_id):
    """Delete a meeting and all associated cards"""
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404
    
    db.session.delete(meeting)
    db.session.commit()
    
    return '', 204

@bp.route('/<int:meeting_id>/reextract', methods=['POST'])
def reextract_cards(meeting_id):
    """
    Re-extract cards from meeting transcript.
    Useful when user wants to extract different card types.
    """
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404
    
    data = request.get_json()
    requested_card_types = [CardType(t) for t in data.get('requested_card_types', [])]
    
    # Get or create canvas
    canvas = Canvas.query.filter_by(meeting_id=meeting_id).first()
    if not canvas:
        canvas = Canvas(
            meeting_id=meeting.id,
            title=f"{meeting.title} - Canvas",
            description="Main canvas for meeting cards"
        )
        db.session.add(canvas)
        db.session.flush()
    
    # Extract new cards using Gemini LLM
    try:
        extraction_service = get_extraction_service()
    except ValueError as e:
        logger.error(f"Failed to initialize extraction service: {e}")
        return jsonify({
            'error': 'LLM service not configured',
            'message': str(e)
        }), 500
    
    extracted_cards = extraction_service.extract_cards(
        transcript=meeting.transcript,
        agenda_items=meeting.agenda_items,
        requested_types=requested_card_types
    )
    
    # Delete old generated cards
    Card.query.filter_by(meeting_id=meeting_id, is_generated=True).delete()
    
    # Create new card records
    for card_data in extracted_cards:
        card = Card(
            meeting_id=meeting.id,
            canvas_id=canvas.id,
            card_type=card_data["type"],
            title=card_data["title"],
            content=card_data["content"],
            is_generated=True,
            transcript_segment=card_data.get("segment"),
            position_x=card_data.get("position_x", 0),
            position_y=card_data.get("position_y", 0)
        )
        db.session.add(card)
    
    db.session.commit()
    
    return jsonify(meeting_detail_schema.dump(meeting))
