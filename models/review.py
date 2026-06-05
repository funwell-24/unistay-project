# models/review.py
from datetime import datetime

class Review:
    """Review and rating model for properties"""
    
    def __init__(self, id=None, property_id=None, student_id=None, rating=None,
                 comment=None, is_approved=False, created_at=None):
        self.id = id
        self.property_id = property_id
        self.student_id = student_id
        self.rating = rating  # 1-5
        self.comment = comment
        self.is_approved = is_approved
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        """Convert review object to dictionary"""
        return {
            'id': self.id,
            'property_id': self.property_id,
            'student_id': self.student_id,
            'rating': self.rating,
            'comment': self.comment,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_star_rating(rating):
        """Generate HTML for star rating"""
        stars = ''
        for i in range(5):
            if i < rating:
                stars += '<i class="fas fa-star text-warning"></i>'
            else:
                stars += '<i class="far fa-star text-warning"></i>'
        return stars