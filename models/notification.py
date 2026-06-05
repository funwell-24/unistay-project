# models/notification.py
from datetime import datetime

class Notification:
    """Notification model for user alerts"""
    
    def __init__(self, id=None, user_id=None, title=None, message=None,
                 type='system', is_read=False, link=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.message = message
        self.type = type  # 'booking', 'message', 'alert', 'system', 'promotion'
        self.is_read = is_read
        self.link = link
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        """Convert notification object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'link': self.link,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_type_icon(notification_type):
        """Get icon for notification type"""
        icons = {
            'booking': 'fas fa-calendar-check',
            'message': 'fas fa-envelope',
            'alert': 'fas fa-bell',
            'system': 'fas fa-cog',
            'promotion': 'fas fa-tag'
        }
        return icons.get(notification_type, 'fas fa-bell')