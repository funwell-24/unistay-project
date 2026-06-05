# blueprints/student.py
from flask import Blueprint, render_template, flash, redirect, url_for, request, session, jsonify
from utils.decorators import login_required, student_required
from app import get_db_connection
from datetime import datetime

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Student dashboard"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return render_template('student/dashboard.html', 
                             saved_count=0, bookings_count=0, recent_bookings=[], 
                             recommended=[], properties_viewed=0, active_bookings=0, 
                             reviews_count=0, unread_messages=0)
    
    try:
        with connection.cursor() as cursor:
            # Get saved properties count
            cursor.execute("SELECT COUNT(*) as count FROM saved_properties WHERE student_id = %s", (session['user_id'],))
            saved_count = cursor.fetchone()['count']
            
            # Get bookings count
            cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE student_id = %s", (session['user_id'],))
            bookings_count = cursor.fetchone()['count']
            
            # Get active bookings count
            cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE student_id = %s AND status = 'approved'", (session['user_id'],))
            active_bookings = cursor.fetchone()['count']
            
            # Get reviews count
            cursor.execute("SELECT COUNT(*) as count FROM reviews WHERE student_id = %s", (session['user_id'],))
            reviews_count = cursor.fetchone()['count']
            
            # Get recent bookings
            cursor.execute("""
                SELECT b.*, p.title, p.location_area 
                FROM bookings b 
                JOIN properties p ON b.property_id = p.id 
                WHERE b.student_id = %s 
                ORDER BY b.created_at DESC 
                LIMIT 5
            """, (session['user_id'],))
            recent_bookings = cursor.fetchall()
            
            # Get recommended properties with images
            cursor.execute("""
                SELECT p.*, u.full_name as landlord_name,
                       (SELECT AVG(rating) FROM reviews WHERE property_id = p.id) as avg_rating,
                       (SELECT media_url FROM property_media WHERE property_id = p.id AND is_primary = TRUE LIMIT 1) as primary_image
                FROM properties p
                JOIN users u ON p.landlord_id = u.id
                WHERE p.status = 'available' AND p.is_approved = TRUE
                ORDER BY p.created_at DESC
                LIMIT 6
            """)
            recommended = cursor.fetchall()
            
            return render_template('student/dashboard.html', 
                                 saved_count=saved_count,
                                 bookings_count=bookings_count,
                                 recent_bookings=recent_bookings,
                                 recommended=recommended,
                                 properties_viewed=0,
                                 active_bookings=active_bookings,
                                 reviews_count=reviews_count,
                                 unread_messages=0)
    except Exception as e:
        print(f"Error in dashboard: {e}")
        flash('Error loading dashboard', 'danger')
        return render_template('student/dashboard.html', 
                             saved_count=0, bookings_count=0, recent_bookings=[], 
                             recommended=[], properties_viewed=0, active_bookings=0, 
                             reviews_count=0, unread_messages=0)
    finally:
        connection.close()
        
@student_bp.route('/properties')
@login_required
@student_required
def properties():
    """Browse properties page"""
    connection = get_db_connection()
    properties = []
    
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT p.*, u.full_name as landlord_name,
                           (SELECT AVG(rating) FROM reviews WHERE property_id = p.id AND is_approved = TRUE) as avg_rating,
                           (SELECT COUNT(*) FROM reviews WHERE property_id = p.id) as review_count,
                           (SELECT media_url FROM property_media WHERE property_id = p.id AND is_primary = TRUE LIMIT 1) as primary_image
                    FROM properties p
                    JOIN users u ON p.landlord_id = u.id
                    WHERE p.status = 'available' AND p.is_approved = TRUE
                    ORDER BY p.created_at DESC
                """)
                properties = cursor.fetchall()
        finally:
            connection.close()
    
    return render_template('student/properties.html', properties=properties)

@student_bp.route('/save-property/<int:property_id>')
@login_required
@student_required
def save_property(property_id):
    """Save a property to favorites"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'error': 'Database connection error'})
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO saved_properties (student_id, property_id) 
                VALUES (%s, %s)
            """, (session['user_id'], property_id))
            connection.commit()
            return jsonify({'success': True, 'message': 'Property saved to favorites!'})
    except:
        return jsonify({'success': False, 'message': 'Property already saved!'})
    finally:
        connection.close()

@student_bp.route('/remove-saved/<int:property_id>')
@login_required
@student_required
def remove_saved(property_id):
    """Remove property from favorites"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('student.saved_properties'))
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM saved_properties 
                WHERE student_id = %s AND property_id = %s
            """, (session['user_id'], property_id))
            connection.commit()
            flash('Property removed from favorites', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('student.saved_properties'))

@student_bp.route('/saved-properties')
@login_required
@student_required
def saved_properties():
    """View saved properties"""
    connection = get_db_connection()
    properties = []
    
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT p.*, u.full_name as landlord_name,
                           (SELECT media_url FROM property_media WHERE property_id = p.id AND is_primary = TRUE LIMIT 1) as primary_image
                    FROM saved_properties sp
                    JOIN properties p ON sp.property_id = p.id
                    JOIN users u ON p.landlord_id = u.id
                    WHERE sp.student_id = %s AND p.is_approved = TRUE
                    ORDER BY sp.saved_at DESC
                """, (session['user_id'],))
                properties = cursor.fetchall()
        finally:
            connection.close()
    
    return render_template('student/saved_properties.html', properties=properties)

@student_bp.route('/bookings')
@login_required
@student_required
def bookings():
    """View booking history"""
    connection = get_db_connection()
    bookings = []
    
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT b.*, p.title, p.location_area, p.monthly_rent, 
                           u.full_name as landlord_name, u.phone as landlord_phone
                    FROM bookings b
                    JOIN properties p ON b.property_id = p.id
                    JOIN users u ON p.landlord_id = u.id
                    WHERE b.student_id = %s
                    ORDER BY b.created_at DESC
                """, (session['user_id'],))
                bookings = cursor.fetchall()
        finally:
            connection.close()
    
    return render_template('student/bookings.html', bookings=bookings)

@student_bp.route('/book-property/<int:property_id>', methods=['POST'])
@login_required
@student_required
def book_property(property_id):
    """Book a property"""
    move_in_date = request.form.get('move_in_date')
    message = request.form.get('message')
    
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('property_detail', property_id=property_id))
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO bookings (property_id, student_id, booking_date, move_in_date, message, status)
                VALUES (%s, %s, CURDATE(), %s, %s, 'pending')
            """, (property_id, session['user_id'], move_in_date, message))
            connection.commit()
            flash('Booking request sent successfully!', 'success')
    except Exception as e:
        flash(f'Error creating booking request: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('property_detail', property_id=property_id))

@student_bp.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
@student_required
def cancel_booking(booking_id):
    """Cancel a booking"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'error': 'Database connection error'})
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE bookings 
                SET status = 'cancelled' 
                WHERE id = %s AND student_id = %s
            """, (booking_id, session['user_id']))
            connection.commit()
            return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        connection.close()

@student_bp.route('/messages')
@login_required
@student_required
def messages():
    """Student messages page"""
    connection = get_db_connection()
    conversations = []
    
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT 
                        u.id as user_id, u.full_name as user_name, u.profile_photo,
                        (SELECT message FROM messages WHERE (sender_id = u.id AND receiver_id = %s) OR (sender_id = %s AND receiver_id = u.id) ORDER BY created_at DESC LIMIT 1) as last_message,
                        (SELECT COUNT(*) FROM messages WHERE sender_id = u.id AND receiver_id = %s AND is_read = FALSE) as unread_count
                    FROM messages m
                    JOIN users u ON (m.sender_id = u.id OR m.receiver_id = u.id)
                    WHERE (m.sender_id = %s OR m.receiver_id = %s) AND u.id != %s
                    GROUP BY u.id
                    ORDER BY MAX(m.created_at) DESC
                """, (session['user_id'], session['user_id'], session['user_id'], session['user_id'], session['user_id'], session['user_id']))
                conversations = cursor.fetchall()
        finally:
            connection.close()
    
    return render_template('student/messages.html', conversations=conversations)

@student_bp.route('/reviews')
@login_required
@student_required
def reviews():
    """Student reviews page"""
    connection = get_db_connection()
    reviews_list = []
    
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT r.*, p.title as property_title
                    FROM reviews r
                    JOIN properties p ON r.property_id = p.id
                    WHERE r.student_id = %s
                    ORDER BY r.created_at DESC
                """, (session['user_id'],))
                reviews_list = cursor.fetchall()
        finally:
            connection.close()
    
    return render_template('student/reviews.html', reviews=reviews_list)

@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    """Student profile page with photo upload"""
    connection = get_db_connection()
    
    if request.method == 'POST':
        if not connection:
            flash('Database connection error', 'danger')
            return redirect(url_for('student.profile'))
        
        try:
            with connection.cursor() as cursor:
                # Handle profile photo upload
                profile_photo = request.files.get('profile_photo')
                profile_photo_url = None
                
                if profile_photo and profile_photo.filename:
                    # Save the uploaded file
                    from werkzeug.utils import secure_filename
                    import os
                    import uuid
                    
                    # Create filename with unique ID
                    original_filename = secure_filename(profile_photo.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
                    
                    # Ensure directory exists
                    upload_folder = os.path.join('static/images/uploads/profiles')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    # Save file
                    filepath = os.path.join(upload_folder, unique_filename)
                    profile_photo.save(filepath)
                    
                    # Return relative URL
                    profile_photo_url = f"/static/images/uploads/profiles/{unique_filename}"
                    
                    # Update profile photo in database
                    cursor.execute("UPDATE users SET profile_photo = %s WHERE id = %s", 
                                 (profile_photo_url, session['user_id']))
                    flash('Profile photo updated!', 'success')
                
                # Update other profile fields
                full_name = request.form.get('full_name')
                phone = request.form.get('phone')
                bio = request.form.get('bio')
                
                if full_name:
                    cursor.execute("UPDATE users SET full_name = %s WHERE id = %s", 
                                 (full_name, session['user_id']))
                if phone:
                    cursor.execute("UPDATE users SET phone = %s WHERE id = %s", 
                                 (phone, session['user_id']))
                if bio:
                    cursor.execute("UPDATE users SET bio = %s WHERE id = %s", 
                                 (bio, session['user_id']))
                
                # Handle password change
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                confirm_password = request.form.get('confirm_password')
                
                if current_password and new_password and confirm_password:
                    if new_password != confirm_password:
                        flash('New passwords do not match!', 'danger')
                    elif len(new_password) < 6:
                        flash('Password must be at least 6 characters!', 'danger')
                    else:
                        from werkzeug.security import check_password_hash, generate_password_hash
                        
                        cursor.execute("SELECT password_hash FROM users WHERE id = %s", (session['user_id'],))
                        user = cursor.fetchone()
                        
                        if check_password_hash(user['password_hash'], current_password):
                            hashed_password = generate_password_hash(new_password)
                            cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", 
                                         (hashed_password, session['user_id']))
                            flash('Password changed successfully!', 'success')
                        else:
                            flash('Current password is incorrect', 'danger')
                
                connection.commit()
                if not profile_photo_url:
                    flash('Profile updated successfully!', 'success')
                
        except Exception as e:
            flash(f'Error updating profile: {e}', 'danger')
            print(f"Profile update error: {e}")
        finally:
            connection.close()
        
        return redirect(url_for('student.profile'))
    
    # GET request - fetch user data
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('student.dashboard'))
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()
            return render_template('student/profile.html', current_user=user)
    except Exception as e:
        flash(f'Error loading profile: {e}', 'danger')
        return redirect(url_for('student.dashboard'))
    finally:
        connection.close()

@student_bp.route('/compare')
@login_required
@student_required
def compare():
    """Compare properties page"""
    property_ids = request.args.get('ids', '')
    properties = []
    
    if property_ids:
        ids = property_ids.split(',')
        connection = get_db_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    placeholders = ','.join(['%s'] * len(ids))
                    cursor.execute(f"""
                        SELECT p.*, u.full_name as landlord_name,
                               (SELECT media_url FROM property_media WHERE property_id = p.id AND is_primary = TRUE LIMIT 1) as primary_image,
                               (SELECT AVG(rating) FROM reviews WHERE property_id = p.id) as avg_rating,
                               (SELECT COUNT(*) FROM reviews WHERE property_id = p.id) as review_count,
                               pf.has_security_guards, pf.has_cctv, pf.has_water, pf.has_electricity, pf.has_wifi,
                               pf.has_car_parking, pf.has_motorcycle_parking
                        FROM properties p
                        JOIN users u ON p.landlord_id = u.id
                        LEFT JOIN property_features pf ON p.id = pf.property_id
                        WHERE p.id IN ({placeholders})
                    """, ids)
                    properties = cursor.fetchall()
            finally:
                connection.close()
    
    return render_template('student/compare.html', properties=properties)

@student_bp.route('/report-listing/<int:property_id>', methods=['POST'])
@login_required
@student_required
def report_listing(property_id):
    """Report a fake listing"""
    report_type = request.form.get('report_type')
    description = request.form.get('description')
    
    if not report_type or not description:
        flash('Please provide all report details', 'danger')
        return redirect(url_for('property_detail', property_id=property_id))
    
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('property_detail', property_id=property_id))
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO reports (reporter_id, property_id, report_type, description, status)
                VALUES (%s, %s, %s, %s, 'pending')
            """, (session['user_id'], property_id, report_type, description))
            connection.commit()
            flash('Thank you for your report. Our team will review it.', 'success')
    except Exception as e:
        flash(f'Error submitting report: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('property_detail', property_id=property_id))

@student_bp.route('/send-message', methods=['POST'])
@login_required
@student_required
def send_message():
    """Send message to landlord"""
    receiver_id = request.form.get('receiver_id')
    property_id = request.form.get('property_id')
    message = request.form.get('message')
    
    if not receiver_id or not message:
        flash('Invalid message data', 'danger')
        return redirect(request.referrer or url_for('student.dashboard'))
    
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(request.referrer or url_for('student.dashboard'))
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO messages (sender_id, receiver_id, property_id, message, is_read, created_at)
                VALUES (%s, %s, %s, %s, FALSE, NOW())
            """, (session['user_id'], receiver_id, property_id, message))
            connection.commit()
            flash('Message sent successfully!', 'success')
    except Exception as e:
        flash(f'Error sending message: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(request.referrer or url_for('student.dashboard'))

@student_bp.route('/write-review/<int:property_id>', methods=['POST'])
@login_required
@student_required
def write_review(property_id):
    """Write a review for a property"""
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment')
    
    if rating < 1 or rating > 5:
        flash('Please select a valid rating (1-5)', 'danger')
        return redirect(url_for('property_detail', property_id=property_id))
    
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'danger')
        return redirect(url_for('property_detail', property_id=property_id))
    
    try:
        with connection.cursor() as cursor:
            # Check if already reviewed
            cursor.execute("SELECT id FROM reviews WHERE property_id = %s AND student_id = %s", 
                         (property_id, session['user_id']))
            if cursor.fetchone():
                flash('You have already reviewed this property!', 'warning')
                return redirect(url_for('property_detail', property_id=property_id))
            
            cursor.execute("""
                INSERT INTO reviews (property_id, student_id, rating, comment, is_approved, created_at)
                VALUES (%s, %s, %s, %s, FALSE, NOW())
            """, (property_id, session['user_id'], rating, comment))
            connection.commit()
            flash('Review submitted! It will be visible after approval.', 'success')
    except Exception as e:
        flash(f'Error submitting review: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('property_detail', property_id=property_id))