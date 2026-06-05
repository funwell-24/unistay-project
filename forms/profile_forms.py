# forms/profile_forms.py
from wtforms import StringField, TextAreaField, FileField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp, EqualTo
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired

class ProfileForm(FlaskForm):
    """Form for updating user profile"""
    
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=3, max=100, message='Name must be between 3 and 100 characters')
    ])
    
    phone = StringField('Phone Number', validators=[
        DataRequired(message='Phone number is required'),
        Length(min=10, max=15),
        Regexp(r'^\+?[0-9\s\-\(\)]+$', message='Please enter a valid phone number')
    ])
    
    profile_photo = FileField('Profile Photo', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    
    bio = TextAreaField('Bio', validators=[
        Optional(),
        Length(max=500, message='Bio must be less than 500 characters')
    ])


class ChangePasswordForm(FlaskForm):
    """Form for changing password"""
    
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ])
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=6, message='Password must be at least 6 characters'),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)', 
               message='Password must contain at least one letter and one number')
    ])
    
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('new_password', message='Passwords must match')
    ])


class LandlordVerificationForm(FlaskForm):
    """Form for landlord verification"""
    
    national_id = StringField('National ID Number', validators=[
        DataRequired(message='National ID is required'),
        Length(min=5, max=20, message='Please enter a valid National ID')
    ])
    
    kra_pin = StringField('KRA PIN', validators=[
        DataRequired(message='KRA PIN is required'),
        Length(min=5, max=15, message='Please enter a valid KRA PIN')
    ])
    
    business_permit = FileField('Business Permit (Optional)', validators=[
        Optional(),
        FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF or Images only!')
    ])
    
    national_id_photo = FileField('National ID Photo', validators=[
        FileRequired(message='Please upload a photo of your National ID'),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])


class ContactForm(FlaskForm):
    """Contact form for website visitors"""
    
    name = StringField('Your Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=100)
    ])
    
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    
    subject = StringField('Subject', validators=[
        DataRequired(message='Subject is required'),
        Length(max=200)
    ])
    
    message = TextAreaField('Message', validators=[
        DataRequired(message='Message is required'),
        Length(min=10, max=2000, message='Message must be between 10 and 2000 characters')
    ])


class ReportForm(FlaskForm):
    """Form for reporting fake listings"""
    
    report_type = SelectField('Report Type', choices=[
        ('fake_listing', 'Fake Listing'),
        ('scam', 'Scam/Fraud'),
        ('misleading_info', 'Misleading Information'),
        ('price_mismatch', 'Price Mismatch'),
        ('other', 'Other')
    ], validators=[DataRequired(message='Please select a report type')])
    
    description = TextAreaField('Description', validators=[
        DataRequired(message='Please provide details about your report'),
        Length(min=20, max=1000, message='Description must be between 20 and 1000 characters')
    ])