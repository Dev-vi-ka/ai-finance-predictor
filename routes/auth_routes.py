from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_model import create_user, get_user_by_email

auth_bp = Blueprint('auth', __name__)


# ---------- REGISTER ----------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if get_user_by_email(email):
            flash("Email already registered", "danger")
            return redirect(url_for('auth.register'))

        password_hash = generate_password_hash(password)
        create_user(name, email, password_hash)

        flash("Registration successful. Please login.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# ---------- LOGIN ----------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

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
