# forms/__init__.py
# This file makes the forms directory a Python package

from forms.auth_forms import LoginForm, RegistrationForm, ForgotPasswordForm
from forms.property_forms import PropertyForm, PropertySearchForm
from forms.profile_forms import ProfileForm, LandlordVerificationForm

__all__ = [
    'LoginForm',
    'RegistrationForm',
    'ForgotPasswordForm',
    'PropertyForm',
    'PropertySearchForm',
    'ProfileForm',
    'LandlordVerificationForm'
]