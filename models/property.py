# models/property.py
from datetime import datetime

class Property:
    """Property model for house listings"""
    
    def __init__(self, id=None, landlord_id=None, title=None, property_type=None,
                 description=None, location_area=None, location_street=None,
                 nearby_landmarks=None, distance_from_campus=None, monthly_rent=None,
                 deposit_amount=None, booking_fee=None, water_charges='included',
                 electricity_charges='separate', status='available', number_of_units=1,
                 available_units=1, is_approved=False, views_count=0, created_at=None):
        self.id = id
        self.landlord_id = landlord_id
        self.title = title
        self.property_type = property_type  # 'bedsitter', 'single_room', 'double_room', 'one_bedroom', 'two_bedroom', 'shared_apartment', 'hostel_room'
        self.description = description
        self.location_area = location_area
        self.location_street = location_street
        self.nearby_landmarks = nearby_landmarks
        self.distance_from_campus = distance_from_campus  # '200m', '500m', '1km', '2km', '3km+'
        self.monthly_rent = monthly_rent
        self.deposit_amount = deposit_amount
        self.booking_fee = booking_fee
        self.water_charges = water_charges  # 'included', 'separate'
        self.electricity_charges = electricity_charges  # 'included', 'separate'
        self.status = status  # 'available', 'occupied', 'reserved', 'under_maintenance'
        self.number_of_units = number_of_units
        self.available_units = available_units
        self.is_approved = is_approved
        self.views_count = views_count
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        """Convert property object to dictionary"""
        return {
            'id': self.id,
            'landlord_id': self.landlord_id,
            'title': self.title,
            'property_type': self.property_type,
            'description': self.description,
            'location_area': self.location_area,
            'location_street': self.location_street,
            'nearby_landmarks': self.nearby_landmarks,
            'distance_from_campus': self.distance_from_campus,
            'monthly_rent': float(self.monthly_rent) if self.monthly_rent else None,
            'deposit_amount': float(self.deposit_amount) if self.deposit_amount else None,
            'booking_fee': float(self.booking_fee) if self.booking_fee else None,
            'water_charges': self.water_charges,
            'electricity_charges': self.electricity_charges,
            'status': self.status,
            'number_of_units': self.number_of_units,
            'available_units': self.available_units,
            'is_approved': self.is_approved,
            'views_count': self.views_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PropertyFeatures:
    """Property features and amenities model"""
    
    def __init__(self, id=None, property_id=None, has_security_guards=False,
                 has_cctv=False, has_electric_fence=False, has_gated_compound=False,
                 has_water=True, has_borehole_water=False, has_electricity=True,
                 has_backup_generator=False, has_wifi=False, wifi_price=None,
                 has_car_parking=False, has_motorcycle_parking=False, parking_fee=None,
                 has_balcony=False, has_wardrobes=True, has_kitchen_cabinets=False,
                 has_hot_shower=False, has_laundry_area=False, has_furniture=False,
                 pet_friendly=False, has_swimming_pool=False, has_gym=False):
        self.id = id
        self.property_id = property_id
        # Security
        self.has_security_guards = has_security_guards
        self.has_cctv = has_cctv
        self.has_electric_fence = has_electric_fence
        self.has_gated_compound = has_gated_compound
        # Utilities
        self.has_water = has_water
        self.has_borehole_water = has_borehole_water
        self.has_electricity = has_electricity
        self.has_backup_generator = has_backup_generator
        self.has_wifi = has_wifi
        self.wifi_price = wifi_price
        # Parking
        self.has_car_parking = has_car_parking
        self.has_motorcycle_parking = has_motorcycle_parking
        self.parking_fee = parking_fee
        # Comfort
        self.has_balcony = has_balcony
        self.has_wardrobes = has_wardrobes
        self.has_kitchen_cabinets = has_kitchen_cabinets
        self.has_hot_shower = has_hot_shower
        self.has_laundry_area = has_laundry_area
        self.has_furniture = has_furniture
        # Additional
        self.pet_friendly = pet_friendly
        self.has_swimming_pool = has_swimming_pool
        self.has_gym = has_gym


class PropertyMedia:
    """Property images and videos model"""
    
    def __init__(self, id=None, property_id=None, media_url=None,
                 media_type='image', is_primary=False, sort_order=0):
        self.id = id
        self.property_id = property_id
        self.media_url = media_url
        self.media_type = media_type  # 'image', 'video'
        self.is_primary = is_primary
        self.sort_order = sort_order


class PropertyRule:
    """Property rules model"""
    
    def __init__(self, id=None, property_id=None, rule_text=None):
        self.id = id
        self.property_id = property_id
        self.rule_text = rule_text