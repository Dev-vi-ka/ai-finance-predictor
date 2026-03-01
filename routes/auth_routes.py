from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_model import create_user, get_user_by_email
from utils.auth_utils import validate_user_registration, sanitize_string

auth_bp = Blueprint('auth', __name__)


# ---------- REGISTER ----------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        # Validate input
        valid, errors = validate_user_registration(name, email, password, password_confirm)
        if not valid:
            for error in errors:
                flash(error, "danger")
            return redirect(url_for('auth.register'))

        # Check if email already registered
        if get_user_by_email(email):
            flash("Email already registered", "danger")
            return redirect(url_for('auth.register'))

        try:
            # Sanitize name
            name = sanitize_string(name, 100)
            password_hash = generate_password_hash(password)
            create_user(name, email, password_hash)
            
            flash("Registration successful. Please login.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f"Registration error: {str(e)}", "danger")
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')


# ---------- LOGIN ----------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash("Email and password are required", "danger")
            return redirect(url_for('auth.login'))

        user = get_user_by_email(email)

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']

            flash("Login successful", "success")
            return redirect(url_for('dashboard.index'))

        flash("Invalid email or password", "danger")

    return render_template('auth/login.html')


# ---------- LOGOUT ----------
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for('auth.login'))
