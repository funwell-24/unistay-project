# models/user.py
from datetime import datetime
import bcrypt

class User:
    """User model representing students, landlords, and admins"""
    
    def __init__(self, id=None, full_name=None, email=None, phone=None, 
                 password_hash=None, user_type=None, is_verified=False, 
                 is_active=True, national_id=None, kra_pin=None, 
                 profile_photo=None, created_at=None):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.password_hash = password_hash
        self.user_type = user_type  # 'student', 'landlord', 'admin'
        self.is_verified = is_verified
        self.is_active = is_active
        self.national_id = national_id
        self.kra_pin = kra_pin
        self.profile_photo = profile_photo
        self.created_at = created_at or datetime.now()
    
    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password, hashed):
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'user_type': self.user_type,
            'is_verified': self.is_verified,
            'is_active': self.is_active,
            'profile_photo': self.profile_photo,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def from_dict(data):
        """Create user object from dictionary"""
        return User(
            id=data.get('id'),
            full_name=data.get('full_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            password_hash=data.get('password_hash'),
            user_type=data.get('user_type'),
            is_verified=data.get('is_verified', False),
            is_active=data.get('is_active', True),
            national_id=data.get('national_id'),
            kra_pin=data.get('kra_pin'),
            profile_photo=data.get('profile_photo'),
            created_at=data.get('created_at')
        )


class VerificationRequest:
    """Model for landlord verification requests"""
    
    def __init__(self, id=None, landlord_id=None, national_id_image=None,
                 kra_pin_image=None, business_permit_image=None, status='pending',
                 admin_notes=None, verified_by=None, verified_at=None, created_at=None):
        self.id = id
        self.landlord_id = landlord_id
        self.national_id_image = national_id_image
        self.kra_pin_image = kra_pin_image
        self.business_permit_image = business_permit_image
        self.status = status  # 'pending', 'approved', 'rejected'
        self.admin_notes = admin_notes
        self.verified_by = verified_by
        self.verified_at = verified_at
        self.created_at = created_at or datetime.now()