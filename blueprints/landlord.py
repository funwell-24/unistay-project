
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from utils.decorators import login_required, landlord_required
from app import get_db_connection
import os
from werkzeug.utils import secure_filename
import uuid
from flask import jsonify

landlord_bp = Blueprint('landlord', __name__)

# Helper function to save uploaded file
def save_uploaded_file(file, folder='profiles'):
    if file and file.filename:
        # Create filename with unique ID
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        
        # Ensure directory exists
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_path, exist_ok=True)
        
        # Save file
        filepath = os.path.join(upload_path, unique_filename)
        file.save(filepath)
        
        # Return relative URL
        return f"/static/images/uploads/{folder}/{unique_filename}"
    return None

@landlord_bp.route('/dashboard')
@login_required
@landlord_required
def dashboard():
    """Landlord dashboard"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM properties WHERE landlord_id = %s", (session['user_id'],))
            properties_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM bookings b JOIN properties p ON b.property_id = p.id WHERE p.landlord_id = %s AND b.status = 'pending'", (session['user_id'],))
            pending_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT SUM(available_units) as total FROM properties WHERE landlord_id = %s", (session['user_id'],))
            available = cursor.fetchone()
            available_units = available['total'] if available['total'] else 0
            
            cursor.execute("""
                SELECT b.*, p.title, u.full_name as student_name
                FROM bookings b
                JOIN properties p ON b.property_id = p.id
                JOIN users u ON b.student_id = u.id
                WHERE p.landlord_id = %s AND b.status = 'pending'
                ORDER BY b.created_at DESC
                LIMIT 10
            """, (session['user_id'],))
            pending_bookings = cursor.fetchall()
            
            return render_template('landlord/dashboard.html', 
                                 properties_count=properties_count,
                                 available_units=available_units,
                                 pending_bookings_count=pending_count,
                                 pending_bookings=pending_bookings)
    except Exception as e:
        print(f"Error in dashboard: {e}")
        return render_template('landlord/dashboard.html', 
                             properties_count=0,
                             available_units=0,
                             pending_bookings_count=0,
                             pending_bookings=[])
    finally:
        connection.close()

@landlord_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@landlord_required
def profile():
    """Landlord profile with photo upload"""
    connection = get_db_connection()
    
    if request.method == 'POST':
        try:
            # Handle profile photo upload
            profile_photo = request.files.get('profile_photo')
            profile_photo_url = None
            
            if profile_photo and profile_photo.filename:
                profile_photo_url = save_uploaded_file(profile_photo, 'profiles')
            
            # Update user information
            with connection.cursor() as cursor:
                if profile_photo_url:
                    cursor.execute("""
                        UPDATE users 
                        SET full_name = %s, phone = %s, profile_photo = %s 
                        WHERE id = %s
                    """, (request.form.get('full_name'), 
                          request.form.get('phone'), 
                          profile_photo_url, 
                          session['user_id']))
                else:
                    cursor.execute("""
                        UPDATE users 
                        SET full_name = %s, phone = %s 
                        WHERE id = %s
                    """, (request.form.get('full_name'), 
                          request.form.get('phone'), 
                          session['user_id']))
                
                # Handle password change
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                
                if current_password and new_password:
                    # Get current password hash
                    cursor.execute("SELECT password_hash FROM users WHERE id = %s", (session['user_id'],))
                    user = cursor.fetchone()
                    
                    from werkzeug.security import check_password_hash, generate_password_hash
                    if check_password_hash(user['password_hash'], current_password):
                        hashed_password = generate_password_hash(new_password)
                        cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", 
                                     (hashed_password, session['user_id']))
                        flash('Password changed successfully!', 'success')
                    else:
                        flash('Current password is incorrect', 'danger')
                
                connection.commit()
                flash('Profile updated successfully!', 'success')
                
        except Exception as e:
            flash(f'Error updating profile: {e}', 'danger')
        finally:
            connection.close()
        
        return redirect(url_for('landlord.profile'))
    
    # GET request - fetch user data
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()
            return render_template('landlord/profile.html', current_user=user)
    finally:
        connection.close()


@landlord_bp.route('/property-bookings')
@login_required
@landlord_required
def property_bookings():
    """View all booking requests for landlord's properties"""
    connection = get_db_connection()
    status = request.args.get('status', 'all')
    
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT b.*, p.title, u.full_name as student_name, 
                       u.email as student_email, u.phone as student_phone, p.id as property_id
                FROM bookings b
                JOIN properties p ON b.property_id = p.id
                JOIN users u ON b.student_id = u.id
                WHERE p.landlord_id = %s
            """
            params = [session['user_id']]
            
            if status != 'all':
                sql += " AND b.status = %s"
                params.append(status)
            
            sql += " ORDER BY b.created_at DESC"
            
            cursor.execute(sql, params)
            bookings = cursor.fetchall()
            
            return render_template('landlord/property_bookings.html', 
                                 bookings=bookings, 
                                 current_status=status)
    except Exception as e:
        print(f"Error in property_bookings: {e}")
        flash('Error loading bookings', 'danger')
        return render_template('landlord/property_bookings.html', bookings=[])
    finally:
        connection.close()


@landlord_bp.route('/approve-booking/<int:booking_id>')
@login_required
@landlord_required
def approve_booking(booking_id):
    """Approve a booking request"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Check if booking belongs to landlord's property
            cursor.execute("""
                UPDATE bookings b
                JOIN properties p ON b.property_id = p.id
                SET b.status = 'approved'
                WHERE b.id = %s AND p.landlord_id = %s
            """, (booking_id, session['user_id']))
            
            if cursor.rowcount > 0:
                connection.commit()
                flash('Booking approved successfully!', 'success')
                
                # Get student info to send notification
                cursor.execute("""
                    SELECT u.email, u.full_name, p.title 
                    FROM bookings b
                    JOIN users u ON b.student_id = u.id
                    JOIN properties p ON b.property_id = p.id
                    WHERE b.id = %s
                """, (booking_id,))
                booking_info = cursor.fetchone()
                
                # Here you can add email notification logic
                print(f"Booking approved for {booking_info['full_name']} - {booking_info['title']}")
            else:
                flash('Booking not found or unauthorized', 'danger')
    except Exception as e:
        flash(f'Error approving booking: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('landlord.property_bookings'))


@landlord_bp.route('/reject-booking/<int:booking_id>')
@login_required
@landlord_required
def reject_booking(booking_id):
    """Reject a booking request"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE bookings b
                JOIN properties p ON b.property_id = p.id
                SET b.status = 'rejected'
                WHERE b.id = %s AND p.landlord_id = %s
            """, (booking_id, session['user_id']))
            
            if cursor.rowcount > 0:
                connection.commit()
                flash('Booking rejected', 'info')
            else:
                flash('Booking not found or unauthorized', 'danger')
    except Exception as e:
        flash(f'Error rejecting booking: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('landlord.property_bookings'))

@landlord_bp.route('/analytics')
@login_required
@landlord_required
def analytics():
    """View analytics for landlord's properties"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Get total properties count
            cursor.execute("SELECT COUNT(*) as count FROM properties WHERE landlord_id = %s", (session['user_id'],))
            total_properties = cursor.fetchone()['count']
            
            # Get total views (from property_views table)
            cursor.execute("""
                SELECT COUNT(*) as count FROM property_views pv
                JOIN properties p ON pv.property_id = p.id
                WHERE p.landlord_id = %s
            """, (session['user_id'],))
            total_views = cursor.fetchone()['count'] or 0
            
            # Get total bookings
            cursor.execute("""
                SELECT COUNT(*) as count FROM bookings b
                JOIN properties p ON b.property_id = p.id
                WHERE p.landlord_id = %s
            """, (session['user_id'],))
            total_bookings = cursor.fetchone()['count'] or 0
            
            # Calculate conversion rate
            conversion_rate = 0
            if total_views > 0:
                conversion_rate = round((total_bookings / total_views) * 100, 1)
            
            # Get top performing properties
            cursor.execute("""
                SELECT p.id, p.title, p.views_count,
                       (SELECT COUNT(*) FROM bookings WHERE property_id = p.id) as bookings_count,
                       (SELECT COUNT(*) FROM property_views WHERE property_id = p.id) as views
                FROM properties p
                WHERE p.landlord_id = %s
                ORDER BY views DESC
                LIMIT 5
            """, (session['user_id'],))
            top_properties = cursor.fetchall()
            
            # Get chart data for last 30 days
            cursor.execute("""
                SELECT DATE(pv.viewed_at) as date, COUNT(*) as count
                FROM property_views pv
                JOIN properties p ON pv.property_id = p.id
                WHERE p.landlord_id = %s 
                    AND pv.viewed_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY DATE(pv.viewed_at)
                ORDER BY date ASC
            """, (session['user_id'],))
            chart_data = cursor.fetchall()
            
            # Prepare chart labels and data
            chart_labels = [row['date'].strftime('%Y-%m-%d') for row in chart_data]
            chart_values = [row['count'] for row in chart_data]
            
            return render_template('landlord/analytics.html',
                                 total_properties=total_properties,
                                 total_views=total_views,
                                 total_bookings=total_bookings,
                                 conversion_rate=conversion_rate,
                                 top_properties=top_properties,
                                 chart_labels=chart_labels,
                                 chart_data=chart_values)
    except Exception as e:
        print(f"Error in analytics: {e}")
        return render_template('landlord/analytics.html',
                             total_properties=0,
                             total_views=0,
                             total_bookings=0,
                             conversion_rate=0,
                             top_properties=[],
                             chart_labels=[],
                             chart_data=[])
    finally:
        connection.close()


@landlord_bp.route('/settings')
@login_required
@landlord_required
def settings():
    """Account settings"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Get notification settings
            cursor.execute("SELECT * FROM notification_settings WHERE user_id = %s", (session['user_id'],))
            notification_settings = cursor.fetchone()
            if not notification_settings:
                notification_settings = {
                    'notify_bookings': True,
                    'notify_messages': True,
                    'notify_promotions': False,
                    'sms_bookings': False,
                    'sms_urgent': False
                }
            
            # Get privacy settings
            cursor.execute("SELECT * FROM privacy_settings WHERE user_id = %s", (session['user_id'],))
            privacy_settings = cursor.fetchone()
            if not privacy_settings:
                privacy_settings = {
                    'profile_visibility': 'public',
                    'share_analytics': True
                }
            
            # Get security settings
            cursor.execute("SELECT * FROM security_settings WHERE user_id = %s", (session['user_id'],))
            security_settings = cursor.fetchone()
            if not security_settings:
                security_settings = {
                    'two_factor_auth': False,
                    'login_alerts': True
                }
            
            return render_template('landlord/settings.html',
                                 notification_settings=notification_settings,
                                 privacy_settings=privacy_settings,
                                 security_settings=security_settings)
    except Exception as e:
        print(f"Error in settings: {e}")
        # Return default settings if tables don't exist
        return render_template('landlord/settings.html',
                             notification_settings={
                                 'notify_bookings': True,
                                 'notify_messages': True,
                                 'notify_promotions': False,
                                 'sms_bookings': False,
                                 'sms_urgent': False
                             },
                             privacy_settings={
                                 'profile_visibility': 'public',
                                 'share_analytics': True
                             },
                             security_settings={
                                 'two_factor_auth': False,
                                 'login_alerts': True
                             })
    finally:
        connection.close()


@landlord_bp.route('/update-notification-settings', methods=['POST'])
@login_required
@landlord_required
def update_notification_settings():
    """Update notification preferences"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('landlord.settings'))
    
    try:
        with connection.cursor() as cursor:
            # Check if settings exist
            cursor.execute("SELECT id FROM notification_settings WHERE user_id = %s", (session['user_id'],))
            exists = cursor.fetchone()
            
            notify_bookings = request.form.get('notify_bookings') == 'on'
            notify_messages = request.form.get('notify_messages') == 'on'
            notify_promotions = request.form.get('notify_promotions') == 'on'
            sms_bookings = request.form.get('sms_bookings') == 'on'
            sms_urgent = request.form.get('sms_urgent') == 'on'
            
            if exists:
                cursor.execute("""
                    UPDATE notification_settings 
                    SET notify_bookings=%s, notify_messages=%s, notify_promotions=%s,
                        sms_bookings=%s, sms_urgent=%s
                    WHERE user_id=%s
                """, (notify_bookings, notify_messages, notify_promotions, sms_bookings, sms_urgent, session['user_id']))
            else:
                cursor.execute("""
                    INSERT INTO notification_settings 
                    (user_id, notify_bookings, notify_messages, notify_promotions, sms_bookings, sms_urgent)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (session['user_id'], notify_bookings, notify_messages, notify_promotions, sms_bookings, sms_urgent))
            
            connection.commit()
            flash('Notification settings updated!', 'success')
    except Exception as e:
        flash(f'Error updating settings: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('landlord.settings'))

@landlord_bp.route('/update-privacy-settings', methods=['POST'])
@login_required
@landlord_required
def update_privacy_settings():
    """Update privacy preferences"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('landlord.settings'))
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM privacy_settings WHERE user_id = %s", (session['user_id'],))
            exists = cursor.fetchone()
            
            profile_visibility = request.form.get('profile_visibility', 'public')
            share_analytics = request.form.get('share_analytics') == 'on'
            
            if exists:
                cursor.execute("""
                    UPDATE privacy_settings 
                    SET profile_visibility=%s, share_analytics=%s
                    WHERE user_id=%s
                """, (profile_visibility, share_analytics, session['user_id']))
            else:
                cursor.execute("""
                    INSERT INTO privacy_settings (user_id, profile_visibility, share_analytics)
                    VALUES (%s, %s, %s)
                """, (session['user_id'], profile_visibility, share_analytics))
            
            connection.commit()
            flash('Privacy settings updated!', 'success')
    except Exception as e:
        flash(f'Error updating privacy settings: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('landlord.settings'))

@landlord_bp.route('/update-security-settings', methods=['POST'])
@login_required
@landlord_required
def update_security_settings():
    """Update security preferences"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('landlord.settings'))
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM security_settings WHERE user_id = %s", (session['user_id'],))
            exists = cursor.fetchone()
            
            two_factor_auth = request.form.get('two_factor_auth') == 'on'
            login_alerts = request.form.get('login_alerts') == 'on'
            
            if exists:
                cursor.execute("""
                    UPDATE security_settings 
                    SET two_factor_auth=%s, login_alerts=%s
                    WHERE user_id=%s
                """, (two_factor_auth, login_alerts, session['user_id']))
            else:
                cursor.execute("""
                    INSERT INTO security_settings (user_id, two_factor_auth, login_alerts)
                    VALUES (%s, %s, %s)
                """, (session['user_id'], two_factor_auth, login_alerts))
            
            connection.commit()
            flash('Security settings updated!', 'success')
    except Exception as e:
        flash(f'Error updating security settings: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('landlord.settings'))




@landlord_bp.route('/change-plan', methods=['POST'])
@login_required
@landlord_required
def change_plan():
    """Change subscription plan"""
    import json
    data = request.get_json()
    plan = data.get('plan')
    
    if plan not in ['free', 'premium', 'enterprise']:
        return jsonify({'success': False, 'error': 'Invalid plan'})
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Check if subscription exists
            cursor.execute("SELECT id FROM subscriptions WHERE landlord_id = %s", (session['user_id'],))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute("""
                    UPDATE subscriptions 
                    SET plan_type = %s, 
                        start_date = CURDATE(),
                        end_date = DATE_ADD(CURDATE(), INTERVAL 1 MONTH),
                        is_active = TRUE
                    WHERE landlord_id = %s
                """, (plan, session['user_id']))
            else:
                cursor.execute("""
                    INSERT INTO subscriptions (landlord_id, plan_type, start_date, end_date, is_active)
                    VALUES (%s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 1 MONTH), TRUE)
                """, (session['user_id'], plan))
            
            connection.commit()
            return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        connection.close()


# Helper route to get booking message via API
@landlord_bp.route('/api/booking-message/<int:booking_id>')
@login_required
@landlord_required
def get_booking_message(booking_id):
    """Get booking message for modal display"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT b.*, u.full_name as student_name, u.email as student_email, u.phone as student_phone
                FROM bookings b
                JOIN users u ON b.student_id = u.id
                JOIN properties p ON b.property_id = p.id
                WHERE b.id = %s AND p.landlord_id = %s
            """, (booking_id, session['user_id']))
            
            booking = cursor.fetchone()
            if booking:
                return jsonify({
                    'success': True,
                    'student_name': booking['student_name'],
                    'student_email': booking['student_email'],
                    'student_phone': booking['student_phone'],
                    'message': booking.get('message', 'No message provided'),
                    'move_in_date': booking.get('move_in_date').strftime('%Y-%m-%d') if booking.get('move_in_date') else 'Not specified'
                })
            else:
                return jsonify({'success': False, 'error': 'Booking not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        connection.close()

@landlord_bp.route('/properties')
@login_required
@landlord_required
def properties():
    """View landlord's properties with images"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.*, 
                       (SELECT media_url FROM property_media WHERE property_id = p.id AND is_primary = TRUE LIMIT 1) as primary_image
                FROM properties p 
                WHERE p.landlord_id = %s 
                ORDER BY p.created_at DESC
            """, (session['user_id'],))
            properties = cursor.fetchall()
            return render_template('landlord/my_properties.html', properties=properties)
    finally:
        connection.close()

@landlord_bp.route('/add-property', methods=['GET', 'POST'])
@login_required
@landlord_required
def add_property():
    """Add new property with images"""
    if request.method == 'POST':
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Insert property
                sql = """INSERT INTO properties (landlord_id, title, property_type, description, 
                           location_area, monthly_rent, available_units, status, is_approved) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, 'available', FALSE)"""
                cursor.execute(sql, (session['user_id'], 
                                   request.form.get('title'),
                                   request.form.get('property_type'),
                                   request.form.get('description'),
                                   request.form.get('location_area'),
                                   request.form.get('monthly_rent'),
                                   request.form.get('available_units', 1)))
                property_id = cursor.lastrowid
                
                # Handle image uploads
                images = request.files.getlist('images')
                for idx, image in enumerate(images):
                    if image and image.filename:
                        image_url = save_uploaded_file(image, 'properties')
                        if image_url:
                            is_primary = (idx == 0)  # First image is primary
                            cursor.execute("""
                                INSERT INTO property_media (property_id, media_url, media_type, is_primary, sort_order)
                                VALUES (%s, %s, 'image', %s, %s)
                            """, (property_id, image_url, is_primary, idx))
                
                connection.commit()
                flash('Property added successfully! It will be visible after admin approval.', 'success')
                return redirect(url_for('landlord.properties'))
        except Exception as e:
            flash(f'Error adding property: {e}', 'danger')
        finally:
            connection.close()
    return render_template('landlord/add_property.html')

@landlord_bp.route('/edit-property/<int:property_id>', methods=['GET', 'POST'])
@login_required
@landlord_required
def edit_property(property_id):
    """Edit property"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if request.method == 'POST':
                cursor.execute("""UPDATE properties 
                    SET title=%s, description=%s, monthly_rent=%s, available_units=%s 
                    WHERE id=%s AND landlord_id=%s""",
                    (request.form.get('title'), 
                     request.form.get('description'),
                     request.form.get('monthly_rent'),
                     request.form.get('available_units', 1),
                     property_id, 
                     session['user_id']))
                connection.commit()
                flash('Property updated successfully!', 'success')
                return redirect(url_for('landlord.properties'))
            
            cursor.execute("SELECT * FROM properties WHERE id=%s AND landlord_id=%s", 
                          (property_id, session['user_id']))
            property_data = cursor.fetchone()
            
            # Get property images
            cursor.execute("SELECT * FROM property_media WHERE property_id=%s ORDER BY sort_order", (property_id,))
            images = cursor.fetchall()
            
            if not property_data:
                flash('Property not found', 'danger')
                return redirect(url_for('landlord.properties'))
            
            return render_template('landlord/edit_property.html', property=property_data, images=images)
    finally:
        connection.close()

@landlord_bp.route('/delete-property/<int:property_id>')
@login_required
@landlord_required
def delete_property(property_id):
    """Delete property"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM properties WHERE id=%s AND landlord_id=%s", 
                          (property_id, session['user_id']))
            connection.commit()
            flash('Property deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting property: {e}', 'danger')
    finally:
        connection.close()
    return redirect(url_for('landlord.properties'))

# Other routes
@landlord_bp.route('/messages')
@login_required
@landlord_required
def messages():
    return render_template('landlord/messages.html')


@landlord_bp.route('/subscription')
@login_required
@landlord_required
def subscription():
    return render_template('landlord/subscription.html', current_plan='free')



@landlord_bp.route('/deactivate-account', methods=['POST'])
@login_required
@landlord_required
def deactivate_account():
    """Deactivate landlord account"""
    from flask import jsonify
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'error': 'Database connection error'})
    
    try:
        with connection.cursor() as cursor:
            # Deactivate user account
            cursor.execute("UPDATE users SET is_active = FALSE WHERE id = %s", (session['user_id'],))
            # Hide all properties
            cursor.execute("UPDATE properties SET status = 'under_maintenance' WHERE landlord_id = %s", (session['user_id'],))
            connection.commit()
            
            # Clear session
            session.clear()
            return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        connection.close()