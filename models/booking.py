# models/booking.py
from datetime import datetime

class Booking:
    """Booking model for property reservations"""
    
    def __init__(self, id=None, property_id=None, student_id=None, booking_date=None,
                 move_in_date=None, move_out_date=None, status='pending', 
                 message=None, created_at=None):
        self.id = id
        self.property_id = property_id
        self.student_id = student_id
        self.booking_date = booking_date or datetime.now().date()
        self.move_in_date = move_in_date
        self.move_out_date = move_out_date
        self.status = status  # 'pending', 'approved', 'rejected', 'cancelled', 'completed'
        self.message = message
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        """Convert booking object to dictionary"""
        return {
            'id': self.id,
            'property_id': self.property_id,
            'student_id': self.student_id,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'move_in_date': self.move_in_date.isoformat() if self.move_in_date else None,
            'move_out_date': self.move_out_date.isoformat() if self.move_out_date else None,
            'status': self.status,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_status_badge(status):
        """Get Bootstrap badge class for booking status"""
        badges = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'cancelled': 'secondary',
            'completed': 'info'
        }
        return badges.get(status, 'secondary')