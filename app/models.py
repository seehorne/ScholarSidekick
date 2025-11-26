from datetime import datetime
import enum
from app.database import db

class CardType(str, enum.Enum):
    """Types of cards that can be extracted from transcripts"""
    TLDR = "tldr"
    TODO = "todo"
    DECISION = "decision"
    QUESTION = "question"
    ACTION_ITEM = "action_item"
    DISCUSSION_POINT = "discussion_point"
    FOLLOW_UP = "follow_up"
    CUSTOM = "custom"

class CardStatus(str, enum.Enum):
    """Status of cards"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Meeting(db.Model):
    """Meeting model - stores meeting metadata and transcript"""
    __tablename__ = "meetings"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    transcript = db.Column(db.Text, nullable=False)
    agenda_items = db.Column(db.JSON, nullable=True)  # List of agenda items
    uncovered_agenda_items = db.Column(db.JSON, nullable=True)  # Items not covered
    meeting_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cards = db.relationship("Card", back_populates="meeting", cascade="all, delete-orphan")
    canvases = db.relationship("Canvas", back_populates="meeting", cascade="all, delete-orphan")

class Card(db.Model):
    """Card model - extracted or manually created items"""
    __tablename__ = "cards"
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey("meetings.id"), nullable=True)
    canvas_id = db.Column(db.Integer, db.ForeignKey("canvases.id"), nullable=True)
    
    card_type = db.Column(db.Enum(CardType), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(CardStatus), default=CardStatus.DRAFT)
    
    # For tracking extraction source
    is_generated = db.Column(db.Boolean, default=False)  # True if extracted by LLM
    transcript_segment = db.Column(db.Text, nullable=True)  # Original transcript segment
    
    # For linking cards
    parent_card_id = db.Column(db.Integer, db.ForeignKey("cards.id"), nullable=True)
    
    # Metadata
    assigned_to = db.Column(db.String(100), nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    position_x = db.Column(db.Integer, default=0)  # Canvas position
    position_y = db.Column(db.Integer, default=0)  # Canvas position
    tags = db.Column(db.JSON, nullable=True)  # List of tags
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    meeting = db.relationship("Meeting", back_populates="cards")
    canvas = db.relationship("Canvas", back_populates="cards")
    parent_card = db.relationship("Card", remote_side=[id], backref="child_cards")
    updates = db.relationship("CardUpdate", back_populates="card", cascade="all, delete-orphan")

class Canvas(db.Model):
    """Canvas model - workspace for organizing cards"""
    __tablename__ = "canvases"
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey("meetings.id"), nullable=False)
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    meeting = db.relationship("Meeting", back_populates="canvases")
    cards = db.relationship("Card", back_populates="canvas", cascade="all, delete-orphan")

class CardUpdate(db.Model):
    """Card update model - tracks updates and pings between users"""
    __tablename__ = "card_updates"
    
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey("cards.id"), nullable=False)
    
    author = db.Column(db.String(100), nullable=False)  # User who made the update
    content = db.Column(db.Text, nullable=False)
    is_ping = db.Column(db.Boolean, default=False)  # True if this is a ping/notification
    pinged_user = db.Column(db.String(100), nullable=True)  # User being pinged
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    card = db.relationship("Card", back_populates="updates")
