from flask import Blueprint, request, jsonify
from datetime import datetime
from app.database import db
from app.models import Card, CardUpdate as CardUpdateModel, CardType, CardStatus
from app.schemas import CardSchema, CardDetailSchema, CardUpdateSchema

bp = Blueprint('cards', __name__)

card_schema = CardSchema()
cards_schema = CardSchema(many=True)
card_detail_schema = CardDetailSchema()
card_update_schema = CardUpdateSchema()
card_updates_schema = CardUpdateSchema(many=True)

@bp.route('/', methods=['POST'])
def create_card():
    """Create a new card (manually added by user)"""
    data = request.get_json()
    errors = card_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    
    # Parse datetime if it's a string
    if 'due_date' in data and isinstance(data.get('due_date'), str):
        data['due_date'] = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
    
    card = Card(
        meeting_id=data.get('meeting_id'),
        canvas_id=data.get('canvas_id'),
        card_type=CardType(data['card_type']),
        title=data['title'],
        content=data['content'],
        status=CardStatus(data.get('status', CardStatus.DRAFT.value)),
        parent_card_id=data.get('parent_card_id'),
        assigned_to=data.get('assigned_to'),
        due_date=data.get('due_date'),
        position_x=data.get('position_x', 0),
        position_y=data.get('position_y', 0),
        tags=data.get('tags'),
        is_generated=False
    )
    db.session.add(card)
    db.session.commit()
    
    return jsonify(card_schema.dump(card)), 201

@bp.route('/', methods=['GET'])
def list_cards():
    """List cards with optional filters"""
    meeting_id = request.args.get('meeting_id', type=int)
    canvas_id = request.args.get('canvas_id', type=int)
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    
    query = Card.query
    
    if meeting_id is not None:
        query = query.filter_by(meeting_id=meeting_id)
    if canvas_id is not None:
        query = query.filter_by(canvas_id=canvas_id)
    
    cards = query.offset(skip).limit(limit).all()
    return jsonify(cards_schema.dump(cards))

@bp.route('/<int:card_id>', methods=['GET'])
def get_card(card_id):
    """Get a specific card with all updates and child cards"""
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404
    
    return jsonify(card_detail_schema.dump(card))

@bp.route('/<int:card_id>', methods=['PUT'])
def update_card(card_id):
    """Update a card"""
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404
    
    data = request.get_json()
    
    # Parse datetime if it's a string
    if 'due_date' in data and isinstance(data.get('due_date'), str):
        data['due_date'] = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
    
    # Update fields
    for field in ['card_type', 'title', 'content', 'status', 'parent_card_id', 
                  'assigned_to', 'due_date', 'position_x', 'position_y', 'tags']:
        if field in data:
            if field == 'card_type' and data[field]:
                setattr(card, field, CardType(data[field]))
            elif field == 'status' and data[field]:
                setattr(card, field, CardStatus(data[field]))
            else:
                setattr(card, field, data[field])
    
    card.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(card_schema.dump(card))

@bp.route('/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    """Delete a card"""
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404
    
    db.session.delete(card)
    db.session.commit()
    
    return '', 204

@bp.route('/<int:card_id>/updates', methods=['POST'])
def add_card_update(card_id):
    """Add an update/ping to a card"""
    # Verify card exists
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404
    
    data = request.get_json()
    data['card_id'] = card_id
    
    errors = card_update_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    
    # Create update
    card_update = CardUpdateModel(
        card_id=card_id,
        author=data['author'],
        content=data['content'],
        is_ping=data.get('is_ping', False),
        pinged_user=data.get('pinged_user')
    )
    db.session.add(card_update)
    db.session.commit()
    
    return jsonify(card_update_schema.dump(card_update)), 201

@bp.route('/<int:card_id>/updates', methods=['GET'])
def get_card_updates(card_id):
    """Get all updates for a card"""
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404
    
    updates = CardUpdateModel.query.filter_by(card_id=card_id).order_by(
        CardUpdateModel.created_at.desc()
    ).all()
    
    return jsonify(card_updates_schema.dump(updates))

@bp.route('/batch-update-positions', methods=['POST'])
def batch_update_positions():
    """
    Batch update card positions on canvas.
    Expects list of {id: int, position_x: int, position_y: int}
    """
    data = request.get_json()
    
    if not isinstance(data, list):
        return jsonify({"error": "Expected a list of position updates"}), 400
    
    updated_cards = []
    
    for update in data:
        card = Card.query.get(update.get('id'))
        if card:
            card.position_x = update.get('position_x', card.position_x)
            card.position_y = update.get('position_y', card.position_y)
            card.updated_at = datetime.utcnow()
            updated_cards.append(card)
    
    db.session.commit()
    
    return jsonify(cards_schema.dump(updated_cards))
