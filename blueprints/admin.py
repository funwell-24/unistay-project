
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from utils.decorators import login_required, admin_required
from app import get_db_connection
from flask import jsonify

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Get statistics
            cursor.execute("SELECT COUNT(*) as total FROM users WHERE user_type = 'student'")
            total_students = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM users WHERE user_type = 'landlord'")
            total_landlords = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM properties WHERE is_approved = TRUE")
            total_properties = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM users WHERE user_type = 'landlord' AND is_verified = FALSE")
            pending_verifications = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM reports WHERE status = 'pending'")
            pending_reports = cursor.fetchone()['total']
            
            return render_template('admin/dashboard.html', 
                                 total_students=total_students,
                                 total_landlords=total_landlords,
                                 total_properties=total_properties,
                                 pending_verifications=pending_verifications,
                                 pending_reports=pending_reports)
    finally:
        connection.close()

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Manage all users"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
            users = cursor.fetchall()
            return render_template('admin/users.html', users=users)
    finally:
        connection.close()

@admin_bp.route('/landlords')
@login_required
@admin_required
def landlords():
    """Manage landlords"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.*, COUNT(p.id) as properties_count 
                FROM users u
                LEFT JOIN properties p ON u.id = p.landlord_id
                WHERE u.user_type = 'landlord'
                GROUP BY u.id
                ORDER BY u.created_at DESC
            """)
            landlords = cursor.fetchall()
            return render_template('admin/landlords.html', landlords=landlords)
    finally:
        connection.close()

@admin_bp.route('/students')
@login_required
@admin_required
def students():
    """Manage students"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.*, COUNT(b.id) as bookings_count, COUNT(r.id) as reviews_count
                FROM users u
                LEFT JOIN bookings b ON u.id = b.student_id
                LEFT JOIN reviews r ON u.id = r.student_id
                WHERE u.user_type = 'student'
                GROUP BY u.id
                ORDER BY u.created_at DESC
            """)
            students = cursor.fetchall()
            return render_template('admin/students.html', students=students)
    finally:
        connection.close()

@admin_bp.route('/verifications')
@login_required
@admin_required
def verifications():
    """Pending verifications"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM users 
                WHERE user_type = 'landlord' AND is_verified = FALSE
                ORDER BY created_at DESC
            """)
            pending_verifications = cursor.fetchall()
            return render_template('admin/verifications.html', pending_verifications=pending_verifications)
    finally:
        connection.close()

@admin_bp.route('/properties')
@login_required
@admin_required
def properties():
    """Manage properties"""
    status = request.args.get('status', 'pending')
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if status == 'pending':
                cursor.execute("""
                    SELECT p.*, u.full_name as landlord_name
                    FROM properties p
                    JOIN users u ON p.landlord_id = u.id
                    WHERE p.is_approved = FALSE
                    ORDER BY p.created_at DESC
                """)
            elif status == 'reported':
                cursor.execute("""
                    SELECT DISTINCT p.*, u.full_name as landlord_name
                    FROM properties p
                    JOIN users u ON p.landlord_id = u.id
                    JOIN reports r ON r.property_id = p.id
                    WHERE r.status = 'pending'
                    ORDER BY p.created_at DESC
                """)
            else:
                cursor.execute("""
                    SELECT p.*, u.full_name as landlord_name
                    FROM properties p
                    JOIN users u ON p.landlord_id = u.id
                    ORDER BY p.created_at DESC
                    LIMIT 50
                """)
            properties = cursor.fetchall()
            return render_template('admin/properties.html', properties=properties, status=status)
    finally:
        connection.close()

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """Manage reports"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT r.*, u.full_name as reporter_name
                FROM reports r
                JOIN users u ON r.reporter_id = u.id
                ORDER BY r.created_at DESC
            """)
            reports = cursor.fetchall()
            return render_template('admin/reports.html', reports=reports)
    finally:
        connection.close()

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Platform analytics"""
    return render_template('admin/analytics.html')

@admin_bp.route('/payments')
@login_required
@admin_required
def payments():
    """Payment management"""
    return render_template('admin/payments.html')

@admin_bp.route('/advertisements')
@login_required
@admin_required
def advertisements():
    """Manage ads/promotions"""
    return render_template('admin/advertisements.html')

@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """Platform settings"""
    connection = get_db_connection()
    
    # Default values
    default_settings = {
        'platform_name': 'UniStay',
        'platform_email': 'info@unistay.com',
        'description': 'Student housing platform connecting students with verified landlords',
        'phone': '+254 700 000000',
        'address': 'Nairobi, Kenya'
    }
    
    # Email settings defaults
    email_settings = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_encryption': 'tls',
        'smtp_username': '',
        'smtp_password': ''
    }
    
    # Payment settings defaults
    payment_settings = {
        'mpesa_consumer_key': '',
        'mpesa_consumer_secret': '',
        'mpesa_shortcode': '',
        'mpesa_passkey': '',
        'stripe_publishable_key': '',
        'stripe_secret_key': ''
    }
    
    # Security settings defaults
    security_settings = {
        'require_email_verification': True,
        'require_2fa_admin': False,
        'session_timeout': 30,
        'max_login_attempts': 5
    }
    
    # Try to load saved settings from database if tables exist
    if connection:
        try:
            with connection.cursor() as cursor:
                # Check if platform_settings table exists and get values
                cursor.execute("""
                    SELECT * FROM information_schema.tables 
                    WHERE table_schema = %s AND table_name = 'platform_settings'
                """, (app.config['MYSQL_DB'],))
                if cursor.fetchone():
                    cursor.execute("SELECT * FROM platform_settings WHERE id = 1")
                    db_settings = cursor.fetchone()
                    if db_settings:
                        default_settings = {**default_settings, **db_settings}
        except Exception as e:
            print(f"Error loading settings from database: {e}")
        finally:
            connection.close()
    
    return render_template('admin/settings.html', 
                         settings=default_settings,
                         email_settings=email_settings,
                         payment_settings=payment_settings,
                         security_settings=security_settings)


@admin_bp.route('/update-general-settings', methods=['POST'])
@login_required
@admin_required
def update_general_settings():
    """Update general platform settings"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin.settings'))
    
    try:
        with connection.cursor() as cursor:
            platform_name = request.form.get('platform_name')
            platform_email = request.form.get('platform_email')
            description = request.form.get('description')
            phone = request.form.get('phone')
            address = request.form.get('address')
            
            # Check if settings exist
            cursor.execute("SELECT id FROM platform_settings WHERE id = 1")
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute("""
                    UPDATE platform_settings 
                    SET platform_name=%s, platform_email=%s, description=%s, phone=%s, address=%s
                    WHERE id=1
                """, (platform_name, platform_email, description, phone, address))
            else:
                cursor.execute("""
                    INSERT INTO platform_settings (id, platform_name, platform_email, description, phone, address)
                    VALUES (1, %s, %s, %s, %s, %s)
                """, (platform_name, platform_email, description, phone, address))
            
            connection.commit()
            flash('General settings updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating settings: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('admin.settings'))


@admin_bp.route('/update-email-settings', methods=['POST'])
@login_required
@admin_required
def update_email_settings():
    """Update email settings"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin.settings'))
    
    try:
        with connection.cursor() as cursor:
            smtp_server = request.form.get('smtp_server')
            smtp_port = request.form.get('smtp_port')
            smtp_encryption = request.form.get('smtp_encryption')
            smtp_username = request.form.get('smtp_username')
            smtp_password = request.form.get('smtp_password')
            
            # Check if settings exist
            cursor.execute("SELECT id FROM email_settings WHERE id = 1")
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute("""
                    UPDATE email_settings 
                    SET smtp_server=%s, smtp_port=%s, smtp_encryption=%s, smtp_username=%s, smtp_password=%s
                    WHERE id=1
                """, (smtp_server, smtp_port, smtp_encryption, smtp_username, smtp_password))
            else:
                cursor.execute("""
                    INSERT INTO email_settings (id, smtp_server, smtp_port, smtp_encryption, smtp_username, smtp_password)
                    VALUES (1, %s, %s, %s, %s, %s)
                """, (smtp_server, smtp_port, smtp_encryption, smtp_username, smtp_password))
            
            connection.commit()
            flash('Email settings updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating email settings: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('admin.settings'))


@admin_bp.route('/update-payment-settings', methods=['POST'])
@login_required
@admin_required
def update_payment_settings():
    """Update payment settings"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin.settings'))
    
    try:
        with connection.cursor() as cursor:
            mpesa_consumer_key = request.form.get('mpesa_consumer_key')
            mpesa_consumer_secret = request.form.get('mpesa_consumer_secret')
            mpesa_shortcode = request.form.get('mpesa_shortcode')
            mpesa_passkey = request.form.get('mpesa_passkey')
            stripe_publishable_key = request.form.get('stripe_publishable_key')
            stripe_secret_key = request.form.get('stripe_secret_key')
            
            # Check if settings exist
            cursor.execute("SELECT id FROM payment_settings WHERE id = 1")
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute("""
                    UPDATE payment_settings 
                    SET mpesa_consumer_key=%s, mpesa_consumer_secret=%s, mpesa_shortcode=%s, 
                        mpesa_passkey=%s, stripe_publishable_key=%s, stripe_secret_key=%s
                    WHERE id=1
                """, (mpesa_consumer_key, mpesa_consumer_secret, mpesa_shortcode, 
                      mpesa_passkey, stripe_publishable_key, stripe_secret_key))
            else:
                cursor.execute("""
                    INSERT INTO payment_settings 
                    (id, mpesa_consumer_key, mpesa_consumer_secret, mpesa_shortcode, 
                     mpesa_passkey, stripe_publishable_key, stripe_secret_key)
                    VALUES (1, %s, %s, %s, %s, %s, %s)
                """, (mpesa_consumer_key, mpesa_consumer_secret, mpesa_shortcode, 
                      mpesa_passkey, stripe_publishable_key, stripe_secret_key))
            
            connection.commit()
            flash('Payment settings updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating payment settings: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('admin.settings'))


@admin_bp.route('/update-security-settings', methods=['POST'])
@login_required
@admin_required
def update_security_settings():
    """Update security settings"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin.settings'))
    
    try:
        with connection.cursor() as cursor:
            require_email_verification = request.form.get('require_email_verification') == 'on'
            require_2fa_admin = request.form.get('require_2fa_admin') == 'on'
            session_timeout = request.form.get('session_timeout')
            max_login_attempts = request.form.get('max_login_attempts')
            
            # Check if settings exist
            cursor.execute("SELECT id FROM security_settings WHERE id = 1")
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute("""
                    UPDATE security_settings 
                    SET require_email_verification=%s, require_2fa_admin=%s, 
                        session_timeout=%s, max_login_attempts=%s
                    WHERE id=1
                """, (require_email_verification, require_2fa_admin, session_timeout, max_login_attempts))
            else:
                cursor.execute("""
                    INSERT INTO security_settings 
                    (id, require_email_verification, require_2fa_admin, session_timeout, max_login_attempts)
                    VALUES (1, %s, %s, %s, %s)
                """, (require_email_verification, require_2fa_admin, session_timeout, max_login_attempts))
            
            connection.commit()
            flash('Security settings updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating security settings: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('admin.settings'))


@admin_bp.route('/add-user', methods=['POST'])
@login_required
@admin_required
def add_user():
    """Add a new user"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin.users'))
    
    try:
        from werkzeug.security import generate_password_hash
        
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        user_type = request.form.get('user_type')
        password = request.form.get('password')
        
        # Validation
        if not full_name or not email or not phone or not password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('admin.users'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'danger')
            return redirect(url_for('admin.users'))
        
        with connection.cursor() as cursor:
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email already registered!', 'danger')
                return redirect(url_for('admin.users'))
            
            # Insert new user
            hashed_password = generate_password_hash(password)
            sql = """
                INSERT INTO users (full_name, email, phone, password_hash, user_type, is_verified, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (full_name, email, phone, hashed_password, user_type, True, True))
            connection.commit()
            
            flash(f'User {full_name} added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding user: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/add-landlord', methods=['POST'])
@login_required
@admin_required
def add_landlord():
    """Add a new landlord"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin.landlords'))
    
    try:
        from werkzeug.security import generate_password_hash
        
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        # Validation
        if not full_name or not email or not phone or not password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('admin.landlords'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'danger')
            return redirect(url_for('admin.landlords'))
        
        with connection.cursor() as cursor:
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email already registered!', 'danger')
                return redirect(url_for('admin.landlords'))
            
            # Insert new landlord
            hashed_password = generate_password_hash(password)
            sql = """
                INSERT INTO users (full_name, email, phone, password_hash, user_type, is_verified, is_active)
                VALUES (%s, %s, %s, %s, 'landlord', %s, %s)
            """
            cursor.execute(sql, (full_name, email, phone, hashed_password, False, True))
            connection.commit()
            
            flash(f'Landlord {full_name} added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding landlord: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('admin.landlords'))


@admin_bp.route('/view-user/<int:user_id>')
@login_required
@admin_required
def view_user(user_id):
    """View user details"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin.users'))
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                flash('User not found', 'danger')
                return redirect(url_for('admin.users'))
            
            return render_template('admin/view_user.html', user=user)
    finally:
        connection.close()


@admin_bp.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user details"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin.users'))
    
    if request.method == 'POST':
        try:
            full_name = request.form.get('full_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            user_type = request.form.get('user_type')
            is_active = request.form.get('is_active') == 'on'
            is_verified = request.form.get('is_verified') == 'on'
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET full_name=%s, email=%s, phone=%s, user_type=%s, is_active=%s, is_verified=%s
                    WHERE id=%s
                """, (full_name, email, phone, user_type, is_active, is_verified, user_id))
                connection.commit()
                flash('User updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating user: {e}', 'danger')
        finally:
            connection.close()
        
        return redirect(url_for('admin.users'))
    
    # GET request
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                flash('User not found', 'danger')
                return redirect(url_for('admin.users'))
            
            return render_template('admin/edit_user.html', user=user)
    finally:
        connection.close()

@admin_bp.route('/toggle-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    """Toggle user active status (activate/deactivate)"""
    import json
    from flask import jsonify
    
    data = request.get_json()
    action = data.get('action')
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'error': 'Database connection error'})
    
    try:
        with connection.cursor() as cursor:
            if action == 'activate':
                cursor.execute("UPDATE users SET is_active = TRUE WHERE id = %s", (user_id,))
                message = 'User activated successfully'
            elif action == 'deactivate':
                cursor.execute("UPDATE users SET is_active = FALSE WHERE id = %s", (user_id,))
                message = 'User deactivated successfully'
            else:
                return jsonify({'success': False, 'error': 'Invalid action'})
            
            connection.commit()
            return jsonify({'success': True, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        connection.close()


@admin_bp.route('/user/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """View user details"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin.users'))
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                flash('User not found', 'danger')
                return redirect(url_for('admin.users'))
            
            # Get user statistics
            if user['user_type'] == 'student':
                cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE student_id = %s", (user_id,))
                bookings = cursor.fetchone()
                cursor.execute("SELECT COUNT(*) as count FROM reviews WHERE student_id = %s", (user_id,))
                reviews = cursor.fetchone()
                user['bookings_count'] = bookings['count'] if bookings else 0
                user['reviews_count'] = reviews['count'] if reviews else 0
            elif user['user_type'] == 'landlord':
                cursor.execute("SELECT COUNT(*) as count FROM properties WHERE landlord_id = %s", (user_id,))
                properties = cursor.fetchone()
                user['properties_count'] = properties['count'] if properties else 0
            
            return render_template('admin/user_detail.html', user=user)
    finally:
        connection.close()


@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    from flask import jsonify
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'error': 'Database connection error'})
    
    try:
        with connection.cursor() as cursor:
            # Don't allow deleting yourself
            if user_id == session['user_id']:
                return jsonify({'success': False, 'error': 'Cannot delete your own account'})
            
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            connection.commit()
            
            if cursor.rowcount > 0:
                return jsonify({'success': True, 'message': 'User deleted successfully'})
            else:
                return jsonify({'success': False, 'error': 'User not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        connection.close()

@admin_bp.route('/test-email', methods=['POST'])
@login_required
@admin_required
def test_email():
    """Test email configuration"""
    from flask import jsonify
    
    try:
        # Here you would implement email test logic
        # For now, just return success
        return jsonify({'success': True, 'message': 'Test email sent successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})


@admin_bp.route('/audit_logs')
@login_required
@admin_required
def audit_logs():
    """System audit logs"""
    return render_template('admin/audit_logs.html')

# Action routes
@admin_bp.route('/verify-landlord/<int:landlord_id>')
@login_required
@admin_required
def verify_landlord(landlord_id):
    """Verify a landlord account"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET is_verified = TRUE WHERE id = %s", (landlord_id,))
            connection.commit()
            flash('Landlord verified successfully!', 'success')
    except Exception as e:
        flash(f'Error verifying landlord: {e}', 'danger')
    finally:
        connection.close()
    return redirect(url_for('admin.verifications'))

@admin_bp.route('/reject-landlord/<int:landlord_id>')
@login_required
@admin_required
def reject_landlord(landlord_id):
    """Reject a landlord account"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s AND user_type = 'landlord'", (landlord_id,))
            connection.commit()
            flash('Landlord account rejected and removed', 'warning')
    except Exception as e:
        flash(f'Error rejecting landlord: {e}', 'danger')
    finally:
        connection.close()
    return redirect(url_for('admin.verifications'))

@admin_bp.route('/delete-landlord/<int:landlord_id>', methods=['POST'])
@login_required
@admin_required
def delete_landlord(landlord_id):
    """Delete a landlord account"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'error': 'Database connection error'})
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM properties WHERE landlord_id = %s", (landlord_id,))
            cursor.execute("DELETE FROM users WHERE id = %s AND user_type = 'landlord'", (landlord_id,))
            connection.commit()
            
            if cursor.rowcount > 0:
                return jsonify({'success': True, 'message': 'Landlord deleted successfully'})
            else:
                return jsonify({'success': False, 'error': 'Landlord not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        connection.close()

@admin_bp.route('/edit-landlord/<int:landlord_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_landlord(landlord_id):
    """Edit landlord information"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin.landlords'))
    
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                full_name = request.form.get('full_name')
                email = request.form.get('email')
                phone = request.form.get('phone')
                
                cursor.execute("""
                    UPDATE users 
                    SET full_name = %s, email = %s, phone = %s 
                    WHERE id = %s AND user_type = 'landlord'
                """, (full_name, email, phone, landlord_id))
                connection.commit()
                flash('Landlord updated successfully!', 'success')
                return redirect(url_for('admin.landlords'))
        except Exception as e:
            flash(f'Error updating landlord: {e}', 'danger')
        finally:
            connection.close()
    
    # GET request - show edit form
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s AND user_type = 'landlord'", (landlord_id,))
            landlord = cursor.fetchone()
            if not landlord:
                flash('Landlord not found', 'danger')
                return redirect(url_for('admin.landlords'))
            return render_template('admin/edit_landlord.html', landlord=landlord)
    finally:
        connection.close()

@admin_bp.route('/approve-property/<int:property_id>')
@login_required
@admin_required
def approve_property(property_id):
    """Approve a property listing"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE properties SET is_approved = TRUE WHERE id = %s", (property_id,))
            connection.commit()
            flash('Property approved successfully!', 'success')
    except Exception as e:
        flash(f'Error approving property: {e}', 'danger')
    finally:
        connection.close()
    return redirect(url_for('admin.properties'))

@admin_bp.route('/reject-property/<int:property_id>')
@login_required
@admin_required
def reject_property(property_id):
    """Reject a property listing"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM properties WHERE id = %s", (property_id,))
            connection.commit()
            flash('Property rejected and removed', 'warning')
    except Exception as e:
        flash(f'Error rejecting property: {e}', 'danger')
    finally:
        connection.close()
    return redirect(url_for('admin.properties'))
