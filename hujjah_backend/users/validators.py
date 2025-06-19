import re
from django.core.exceptions import ValidationError

def validate_saudi_phone(value):
    pattern = r'^(?:\+9665|05)\d{8}$'
    if not re.match(pattern, value):
        raise ValidationError("Enter a valid Saudi phone number (e.g. +966512345678 or 0551234567)")
