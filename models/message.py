# models/message.py
from datetime import datetime

class Message:
    """Message model for chat between users"""
    
    def __init__(self, id=None, sender_id=None, receiver_id=None, property_id=None,
                 message=None, is_read=False, created_at=None):
        self.id = id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.property_id = property_id
        self.message = message
        self.is_read = is_read
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        """Convert message object to dictionary"""
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'property_id': self.property_id,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def format_time(self):
        """Format message time for display"""
        now = datetime.now()
        if self.created_at.date() == now.date():
            return self.created_at.strftime('%I:%M %p')
        elif (now - self.created_at).days < 7:
            return self.created_at.strftime('%A')
        else:
            return self.created_at.strftime('%b %d')