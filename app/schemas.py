from marshmallow import Schema, fields, validate, EXCLUDE, post_dump
from app.models import CardType, CardStatus

# Meeting Schemas
class MeetingSchema(Schema):
    """Schema for meeting serialization"""
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    transcript = fields.Str(required=True)
    agenda_items = fields.List(fields.Str(), allow_none=True)
    uncovered_agenda_items = fields.List(fields.Str(), allow_none=True, dump_only=True)
    meeting_date = fields.DateTime(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    class Meta:
        unknown = EXCLUDE

class MeetingCreateSchema(Schema):
    """Schema for creating a new meeting"""
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    transcript = fields.Str(required=True)
    agenda_items = fields.List(fields.Str(), allow_none=True)
    meeting_date = fields.DateTime(required=True)
    requested_card_types = fields.List(
        fields.Str(validate=validate.OneOf([t.value for t in CardType])),
        load_default=[CardType.TLDR.value, CardType.TODO.value, CardType.ACTION_ITEM.value]
    )
    
    class Meta:
        unknown = EXCLUDE

# Card Schemas
class CardSchema(Schema):
    """Schema for card serialization"""
    id = fields.Int(dump_only=True)
    meeting_id = fields.Int(allow_none=True)
    canvas_id = fields.Int(allow_none=True)
    card_type = fields.Method("serialize_card_type", deserialize="deserialize_card_type")
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    status = fields.Method("serialize_status", deserialize="deserialize_status")
    is_generated = fields.Bool(dump_only=True)
    transcript_segment = fields.Str(allow_none=True, dump_only=True)
    parent_card_id = fields.Int(allow_none=True)
    assigned_to = fields.Str(allow_none=True)
    due_date = fields.DateTime(allow_none=True)
    position_x = fields.Int(load_default=0)
    position_y = fields.Int(load_default=0)
    tags = fields.List(fields.Str(), allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    def serialize_card_type(self, obj):
        """Serialize card_type enum to string value"""
        return obj.card_type.value if hasattr(obj.card_type, 'value') else obj.card_type
    
    def deserialize_card_type(self, value):
        """Deserialize card_type string to enum"""
        return CardType(value) if value else None
    
    def serialize_status(self, obj):
        """Serialize status enum to string value"""
        return obj.status.value if hasattr(obj.status, 'value') else obj.status
    
    def deserialize_status(self, value):
        """Deserialize status string to enum"""
        return CardStatus(value) if value else CardStatus.DRAFT
    
    @post_dump
    def serialize_enums(self, data, **kwargs):
        """Convert enum objects to their string values"""
        if 'card_type' in data and hasattr(data['card_type'], 'value'):
            data['card_type'] = data['card_type'].value
        if 'status' in data and hasattr(data['status'], 'value'):
            data['status'] = data['status'].value
        return data
    
    class Meta:
        unknown = EXCLUDE

# Canvas Schemas
class CanvasSchema(Schema):
    """Schema for canvas serialization"""
    id = fields.Int(dump_only=True)
    meeting_id = fields.Int(required=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    cards = fields.List(fields.Nested(CardSchema), dump_only=True)
    
    class Meta:
        unknown = EXCLUDE

# Card Update Schemas
class CardUpdateSchema(Schema):
    """Schema for card update serialization"""
    id = fields.Int(dump_only=True)
    card_id = fields.Int(required=True)
    author = fields.Str(required=True)
    content = fields.Str(required=True)
    is_ping = fields.Bool(load_default=False)
    pinged_user = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    
    class Meta:
        unknown = EXCLUDE

# Extended schemas with relations
class CardDetailSchema(CardSchema):
    """Extended card schema with updates"""
    updates = fields.List(fields.Nested(CardUpdateSchema), dump_only=True)
    child_cards = fields.List(fields.Nested(CardSchema), dump_only=True)

class MeetingDetailSchema(MeetingSchema):
    """Extended meeting schema with cards"""
    cards = fields.List(fields.Nested(CardSchema), dump_only=True)
    canvases = fields.List(fields.Nested(CanvasSchema), dump_only=True)
