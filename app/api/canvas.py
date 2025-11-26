from flask import Blueprint, request, jsonify
from datetime import datetime
from app.database import db
from app.models import Canvas
from app.schemas import CanvasSchema

bp = Blueprint('canvas', __name__)

canvas_schema = CanvasSchema()
canvases_schema = CanvasSchema(many=True)

@bp.route('/', methods=['POST'])
def create_canvas():
    """Create a new canvas"""
    data = request.get_json()
    errors = canvas_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    
    canvas = Canvas(
        meeting_id=data['meeting_id'],
        title=data['title'],
        description=data.get('description')
    )
    db.session.add(canvas)
    db.session.commit()
    
    return jsonify(canvas_schema.dump(canvas)), 201

@bp.route('/', methods=['GET'])
def list_canvases():
    """List all canvases, optionally filtered by meeting"""
    meeting_id = request.args.get('meeting_id', type=int)
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    
    query = Canvas.query
    
    if meeting_id is not None:
        query = query.filter_by(meeting_id=meeting_id)
    
    canvases = query.offset(skip).limit(limit).all()
    return jsonify(canvases_schema.dump(canvases))

@bp.route('/<int:canvas_id>', methods=['GET'])
def get_canvas(canvas_id):
    """Get a specific canvas with all cards"""
    canvas = Canvas.query.get(canvas_id)
    if not canvas:
        return jsonify({"error": "Canvas not found"}), 404
    
    return jsonify(canvas_schema.dump(canvas))

@bp.route('/<int:canvas_id>', methods=['PUT'])
def update_canvas(canvas_id):
    """Update a canvas"""
    canvas = Canvas.query.get(canvas_id)
    if not canvas:
        return jsonify({"error": "Canvas not found"}), 404
    
    data = request.get_json()
    
    for field in ['title', 'description']:
        if field in data:
            setattr(canvas, field, data[field])
    
    canvas.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(canvas_schema.dump(canvas))

@bp.route('/<int:canvas_id>', methods=['DELETE'])
def delete_canvas(canvas_id):
    """Delete a canvas"""
    canvas = Canvas.query.get(canvas_id)
    if not canvas:
        return jsonify({"error": "Canvas not found"}), 404
    
    db.session.delete(canvas)
    db.session.commit()
    
    return '', 204
