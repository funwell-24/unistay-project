
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from utils.decorators import login_required
from app import get_db_connection
import bcrypt

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        connection = get_db_connection()
        if not connection:
            flash('Database connection error. Please try again later.', 'danger')
            return redirect(url_for('auth.login'))
        
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE email = %s AND user_type = %s"
                cursor.execute(sql, (email, user_type))
                user = cursor.fetchone()
                
                if user and verify_password(password, user['password_hash']):
                    session['user_id'] = user['id']
                    session['user_type'] = user['user_type']
                    session['user_name'] = user['full_name']
                    
                    flash(f'Welcome back, {user["full_name"]}!', 'success')
                    
                    if user['user_type'] == 'admin':
                        return redirect(url_for('admin.dashboard'))
                    elif user['user_type'] == 'landlord':
                        if not user['is_verified']:
                            flash('Your account is pending verification.', 'warning')
                        return redirect(url_for('landlord.dashboard'))
                    else:
                        return redirect(url_for('student.dashboard'))
                else:
                    flash('Invalid email or password', 'danger')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')
        finally:
            if connection:
                connection.close()
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        user_type = request.form.get('user_type')
        
        # Validation
        if not full_name or not email or not phone or not password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'danger')
            return redirect(url_for('auth.register'))
        
        connection = get_db_connection()
        if not connection:
            flash('Database connection error. Please try again later.', 'danger')
            return redirect(url_for('auth.register'))
        
        try:
            with connection.cursor() as cursor:
                # Check if email already exists
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('Email already registered!', 'danger')
                    return redirect(url_for('auth.register'))
                
                # Insert new user
                hashed_password = hash_password(password)
                sql = """
                    INSERT INTO users (full_name, email, phone, password_hash, user_type, is_verified)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (full_name, email, phone, hashed_password, user_type, False))
                connection.commit()
                
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Registration error: {str(e)}', 'danger')
        finally:
            if connection:
                connection.close()
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page"""
    if request.method == 'POST':
        email = request.form.get('email')
        flash('Password reset link has been sent to your email.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/landlord-verification', methods=['GET', 'POST'])
@login_required
def landlord_verification():
    """Landlord verification submission"""
    if session.get('user_type') != 'landlord':
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        national_id = request.form.get('national_id')
        kra_pin = request.form.get('kra_pin')
        
        connection = get_db_connection()
        if not connection:
            flash('Database connection error', 'danger')
            return redirect(url_for('landlord.dashboard'))
        
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE users SET national_id = %s, kra_pin = %s WHERE id = %s"
                cursor.execute(sql, (national_id, kra_pin, session['user_id']))
                connection.commit()
                flash('Verification documents submitted successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            if connection:
                connection.close()
        
        return redirect(url_for('landlord.dashboard'))
    
    return render_template('auth/landlord_verification.html')
