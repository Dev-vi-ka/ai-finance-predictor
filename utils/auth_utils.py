"""Authentication and validation utilities."""

import re
from functools import wraps
from flask import request, flash, redirect, url_for
import bleach


# Allowed HTML tags for bleach
ALLOWED_TAGS = []
ALLOWED_ATTRIBUTES = {}


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password):
    """Validate password strength.
    
    Requirements:
    - At least 6 characters
    - At least one letter
    - At least one digit
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    
    if not any(c.isalpha() for c in password):
        return False, "Password must contain at least one letter."
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."
    
    return True, "Password is valid."


def validate_amount(amount):
    """Validate transaction amount."""
    try:
        val = float(amount)
        if val <= 0:
            return False, "Amount must be greater than 0."
        if val > 10000000:  # 10 million limit
            return False, "Amount is too large."
        return True, "Amount is valid."
    except (ValueError, TypeError):
        return False, "Amount must be a valid number."


def validate_date(date_str, format_str='%Y-%m-%d'):
    """Validate date format."""
    from datetime import datetime
    
    try:
        date_obj = datetime.strptime(date_str, format_str)
        # Check it's not a future date
        if date_obj > datetime.now():
            return False, "Date cannot be in the future."
        return True, "Date is valid."
    except ValueError:
        return False, f"Date must be in {format_str} format."


def validate_transaction_input(description, amount, category, date):
    """Validate all transaction input fields."""
    errors = []
    
    # Validate description
    if not description or len(description) < 2:
        errors.append("Description must be at least 2 characters.")
    if len(description) > 255:
        errors.append("Description is too long (max 255 characters).")
    
    # Validate amount
    valid, msg = validate_amount(amount)
    if not valid:
        errors.append(msg)
    
    # Validate category
    if not category or len(category) < 2:
        errors.append("Category must be at least 2 characters.")
    if len(category) > 50:
        errors.append("Category is too long.")
    
    # Validate date
    valid, msg = validate_date(date)
    if not valid:
        errors.append(msg)
    
    return len(errors) == 0, errors


def sanitize_string(text, max_length=255):
    """Sanitize user input to prevent XSS attacks."""
    if not text:
        return ""
    
    # Remove any HTML tags
    text = bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
    
    # Trim whitespace
    text = text.strip()
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text


def validate_user_registration(name, email, password, password_confirm):
    """Validate user registration input."""
    errors = []
    
    # Validate name
    if not name or len(name) < 2:
        errors.append("Name must be at least 2 characters.")
    if len(name) > 100:
        errors.append("Name is too long.")
    
    # Validate email
    if not email or not validate_email(email):
        errors.append("Email is invalid.")
    
    # Validate password
    valid, msg = validate_password(password)
    if not valid:
        errors.append(msg)
    
    # Check password confirmation
    if password != password_confirm:
        errors.append("Passwords do not match.")
    
    return len(errors) == 0, errors


def validate_with_decorator(required_fields=None):
    """Decorator to validate form fields."""
    if required_fields is None:
        required_fields = []
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            for field in required_fields:
                if field not in request.form or not request.form[field].strip():
                    flash(f"{field} is required.", "danger")
                    return redirect(request.referrer or url_for('dashboard.index'))
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator
