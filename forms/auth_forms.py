# forms/auth_forms.py
from wtforms import StringField, PasswordField, SelectField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, Optional
from flask_wtf import FlaskForm

class LoginForm(FlaskForm):
    """Login form for users"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=100, message='Email must be less than 100 characters')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    
    user_type = SelectField('User Type', choices=[
        ('student', 'Student'),
        ('landlord', 'Landlord'),
        ('admin', 'Admin')
    ], validators=[DataRequired(message='Please select user type')])
    
    remember_me = BooleanField('Remember Me')


class RegistrationForm(FlaskForm):
    """Registration form for new users"""
    
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=3, max=100, message='Name must be between 3 and 100 characters'),
        Regexp(r'^[a-zA-Z\s]+$', message='Name can only contain letters and spaces')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=100, message='Email must be less than 100 characters')
    ])
    
    phone = StringField('Phone Number', validators=[
        DataRequired(message='Phone number is required'),
        Length(min=10, max=15, message='Please enter a valid phone number'),
        Regexp(r'^\+?[0-9\s\-\(\)]+$', message='Please enter a valid phone number')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters'),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)', 
               message='Password must contain at least one letter and one number')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    user_type = SelectField('I am a', choices=[
        ('student', 'Student looking for accommodation'),
        ('landlord', 'Landlord with property to rent')
    ], validators=[DataRequired(message='Please select user type')])


class ForgotPasswordForm(FlaskForm):
    """Forgot password form"""
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])


class ResetPasswordForm(FlaskForm):
    """Reset password form"""
    
    password = PasswordField('New Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])