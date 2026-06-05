# models/report.py
from datetime import datetime

class Report:
    """Report model for fake listings and scams"""
    
    def __init__(self, id=None, reporter_id=None, property_id=None, user_id=None,
                 report_type=None, description=None, status='pending',
                 admin_notes=None, resolved_at=None, created_at=None):
        self.id = id
        self.reporter_id = reporter_id
        self.property_id = property_id
        self.user_id = user_id
        self.report_type = report_type  # 'fake_listing', 'scam', 'fraud', 'misleading_info', 'other'
        self.description = description
        self.status = status  # 'pending', 'investigating', 'resolved', 'dismissed'
        self.admin_notes = admin_notes
        self.resolved_at = resolved_at
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        """Convert report object to dictionary"""
        return {
            'id': self.id,
            'reporter_id': self.reporter_id,
            'property_id': self.property_id,
            'user_id': self.user_id,
            'report_type': self.report_type,
            'description': self.description,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_status_badge(status):
        """Get Bootstrap badge class for report status"""
        badges = {
            'pending': 'warning',
            'investigating': 'info',
            'resolved': 'success',
            'dismissed': 'secondary'
        }
        return badges.get(status, 'secondary')