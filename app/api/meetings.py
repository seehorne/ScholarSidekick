from flask import Blueprint, request, jsonify
from datetime import datetime
from app.database import db
from app.models import Meeting, Card, Canvas, CardType
from app.schemas import MeetingSchema, MeetingCreateSchema, MeetingDetailSchema
from app.services.extraction_service import ExtractionService

bp = Blueprint('meetings', __name__)

meeting_schema = MeetingSchema()
meetings_schema = MeetingSchema(many=True)
meeting_create_schema = MeetingCreateSchema()
meeting_detail_schema = MeetingDetailSchema()

@bp.route('/', methods=['POST'])
def create_meeting():
    """
    Create a new meeting and extract cards from transcript.
    
    This endpoint:
    1. Creates a meeting record
    2. Extracts cards based on requested_card_types (placeholder for LLM)
    3. Creates a default canvas
    4. Returns meeting with generated cards
    """
    data = request.get_json()
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
    
    # Extract cards from transcript (placeholder - will use LLM later)
    extraction_service = ExtractionService()
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
    
    # Extract new cards
    extraction_service = ExtractionService()
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
