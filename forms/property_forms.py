# forms/property_forms.py
from wtforms import StringField, TextAreaField, SelectField, DecimalField, IntegerField, BooleanField, FileField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired

class PropertyForm(FlaskForm):
    """Form for adding/editing properties"""
    
    # Basic Information
    title = StringField('Property Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=5, max=200, message='Title must be between 5 and 200 characters')
    ])
    
    property_type = SelectField('Property Type', choices=[
        ('bedsitter', 'Bedsitter'),
        ('single_room', 'Single Room'),
        ('double_room', 'Double Room'),
        ('one_bedroom', 'One Bedroom'),
        ('two_bedroom', 'Two Bedroom'),
        ('shared_apartment', 'Shared Apartment'),
        ('hostel_room', 'Hostel Room')
    ], validators=[DataRequired(message='Please select property type')])
    
    description = TextAreaField('Description', validators=[
        DataRequired(message='Description is required'),
        Length(min=20, max=2000, message='Description must be between 20 and 2000 characters')
    ])
    
    # Location Information
    location_area = StringField('Area/Estate', validators=[
        DataRequired(message='Location area is required'),
        Length(max=100)
    ])
    
    location_street = StringField('Street/Road', validators=[
        Optional(),
        Length(max=100)
    ])
    
    nearby_landmarks = TextAreaField('Nearby Landmarks', validators=[
        Optional(),
        Length(max=500)
    ])
    
    distance_from_campus = SelectField('Distance from Campus', choices=[
        ('200m', '200 meters'),
        ('500m', '500 meters'),
        ('1km', '1 kilometer'),
        ('2km', '2 kilometers'),
        ('3km+', 'More than 3 kilometers')
    ], validators=[DataRequired()])
    
    # Pricing Information
    monthly_rent = DecimalField('Monthly Rent (KES)', validators=[
        DataRequired(message='Monthly rent is required'),
        NumberRange(min=0, message='Rent must be a positive number')
    ], places=2)
    
    deposit_amount = DecimalField('Deposit Amount (KES)', validators=[
        Optional(),
        NumberRange(min=0)
    ], places=2)
    
    booking_fee = DecimalField('Booking Fee (KES)', validators=[
        Optional(),
        NumberRange(min=0)
    ], places=2)
    
    # Availability
    number_of_units = IntegerField('Number of Units', validators=[
        DataRequired(),
        NumberRange(min=1, max=100, message='Number of units must be between 1 and 100')
    ], default=1)
    
    # Utilities
    water_charges = SelectField('Water Charges', choices=[
        ('included', 'Included in Rent'),
        ('separate', 'Separate Payment')
    ])
    
    electricity_charges = SelectField('Electricity Charges', choices=[
        ('included', 'Included in Rent'),
        ('separate', 'Separate Payment')
    ])
    
    # Features (Checkboxes)
    has_security_guards = BooleanField('Security Guards')
    has_cctv = BooleanField('CCTV Cameras')
    has_gated_compound = BooleanField('Gated Compound')
    has_water = BooleanField('Water Available', default=True)
    has_electricity = BooleanField('Electricity Available', default=True)
    has_wifi = BooleanField('WiFi Available')
    has_car_parking = BooleanField('Car Parking')
    has_motorcycle_parking = BooleanField('Motorcycle Parking')
    has_balcony = BooleanField('Balcony')
    has_wardrobes = BooleanField('Wardrobes')
    has_hot_shower = BooleanField('Hot Shower')
    pet_friendly = BooleanField('Pet Friendly')
    
    # Images
    images = FileField('Property Images', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    
    def validate_monthly_rent(self, field):
        """Custom validation for monthly rent"""
        if field.data < 1000:
            raise ValidationError('Monthly rent must be at least 1000 KES')
        if field.data > 500000:
            raise ValidationError('Monthly rent cannot exceed 500,000 KES')


class PropertySearchForm(FlaskForm):
    """Form for searching properties"""
    
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    
    property_type = SelectField('Property Type', choices=[
        ('', 'All Types'),
        ('bedsitter', 'Bedsitter'),
        ('single_room', 'Single Room'),
        ('one_bedroom', 'One Bedroom'),
        ('two_bedroom', 'Two Bedroom')
    ], validators=[Optional()])
    
    min_price = DecimalField('Min Price', validators=[Optional(), NumberRange(min=0)], places=0)
    max_price = DecimalField('Max Price', validators=[Optional(), NumberRange(min=0)], places=0)
    
    distance = SelectField('Max Distance', choices=[
        ('', 'Any Distance'),
        ('200m', '200m'),
        ('500m', '500m'),
        ('1km', '1km'),
        ('2km', '2km')
    ], validators=[Optional()])
    
    has_wifi = BooleanField('WiFi')
    has_security = BooleanField('Security')
    has_parking = BooleanField('Parking')
    has_water = BooleanField('Water')
    has_electricity = BooleanField('Electricity')