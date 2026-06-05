
from flask import Blueprint, jsonify, request, session
from app import get_db_connection
from utils.decorators import login_required

api_bp = Blueprint('api', __name__)

@api_bp.route('/search-properties', methods=['GET'])
def search_properties():
    """API endpoint for property search"""
    location = request.args.get('location', '')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'error': 'Database connection error'})
    
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT id, title, property_type, location_area, monthly_rent, 
                       distance_from_campus, status
                FROM properties
                WHERE status = 'available' AND is_approved = TRUE
            """
            params = []
            
            if location:
                sql += " AND location_area LIKE %s"
                params.append(f'%{location}%')
            if min_price:
                sql += " AND monthly_rent >= %s"
                params.append(min_price)
            if max_price:
                sql += " AND monthly_rent <= %s"
                params.append(max_price)
            
            cursor.execute(sql, params)
            properties = cursor.fetchall()
            
            return jsonify({'success': True, 'properties': properties})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        connection.close()


@api_bp.route('/property/<int:property_id>', methods=['GET'])
def get_property(property_id):
    """Get single property details"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'error': 'Database connection error'})
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.*, u.full_name as landlord_name, u.phone as landlord_phone
                FROM properties p
                JOIN users u ON p.landlord_id = u.id
                WHERE p.id = %s
            """, (property_id,))
            property_data = cursor.fetchone()
            
            if property_data:
                return jsonify({'success': True, 'property': property_data})
            else:
                return jsonify({'success': False, 'error': 'Property not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        connection.close()


@api_bp.route('/send-message', methods=['POST'])
@login_required
def send_message():
    """API endpoint to send a message"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Invalid JSON data'})
        
        receiver_id = data.get('receiver_id')
        message = data.get('message')
        
        if not receiver_id or not message:
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'error': 'Database connection error'})
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO messages (sender_id, receiver_id, message, is_read, created_at)
                    VALUES (%s, %s, %s, FALSE, NOW())
                """, (session['user_id'], receiver_id, message))
                connection.commit()
                
                return jsonify({'success': True, 'message': 'Message sent successfully'})
        finally:
            connection.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@api_bp.route('/messages/<int:user_id>')
@login_required
def get_messages(user_id):
    """API endpoint to get messages between users"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'error': 'Database connection error'})
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT m.*, u.full_name as sender_name, u.profile_photo as sender_photo
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE (m.sender_id = %s AND m.receiver_id = %s) 
                   OR (m.sender_id = %s AND m.receiver_id = %s)
                ORDER BY m.created_at ASC
            """, (session['user_id'], user_id, user_id, session['user_id']))
            
            messages = cursor.fetchall()
            
            # Mark messages as read
            cursor.execute("""
                UPDATE messages SET is_read = TRUE 
                WHERE sender_id = %s AND receiver_id = %s AND is_read = FALSE
            """, (user_id, session['user_id']))
            connection.commit()
            
            # Format datetime for JSON
            for msg in messages:
                if msg.get('created_at'):
                    msg['created_at'] = msg['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return jsonify({'success': True, 'messages': messages})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        connection.close()


@api_bp.route('/conversations')
@login_required
def get_conversations():
    """API endpoint to get user's conversations"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'error': 'Database connection error'})
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT 
                    u.id as user_id, 
                    u.full_name as user_name, 
                    u.profile_photo,
                    (SELECT message FROM messages 
                     WHERE (sender_id = u.id AND receiver_id = %s) 
                        OR (sender_id = %s AND receiver_id = u.id) 
                     ORDER BY created_at DESC LIMIT 1) as last_message,
                    (SELECT created_at FROM messages 
                     WHERE (sender_id = u.id AND receiver_id = %s) 
                        OR (sender_id = %s AND receiver_id = u.id) 
                     ORDER BY created_at DESC LIMIT 1) as last_message_time,
                    (SELECT COUNT(*) FROM messages 
                     WHERE sender_id = u.id AND receiver_id = %s AND is_read = FALSE) as unread_count
                FROM messages m
                JOIN users u ON (m.sender_id = u.id OR m.receiver_id = u.id)
                WHERE (m.sender_id = %s OR m.receiver_id = %s) AND u.id != %s
                GROUP BY u.id
                ORDER BY last_message_time DESC
            """, (session['user_id'], session['user_id'], session['user_id'], 
                  session['user_id'], session['user_id'], session['user_id'], 
                  session['user_id'], session['user_id']))
            
            conversations = cursor.fetchall()
            
            # Format the data
            result = []
            for conv in conversations:
                result.append({
                    'user_id': conv['user_id'],
                    'user_name': conv['user_name'],
                    'profile_photo': conv['profile_photo'],
                    'last_message': conv['last_message'],
                    'last_message_time': conv['last_message_time'].strftime('%Y-%m-%d %H:%M') if conv['last_message_time'] else None,
                    'unread_count': conv['unread_count'] or 0
                })
            
            return jsonify({'success': True, 'conversations': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        connection.close()


@api_bp.route('/booking-message/<int:booking_id>')
@login_required
def get_booking_message(booking_id):
    """API endpoint to get booking message for landlord"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'error': 'Database connection error'})
    
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


@api_bp.route('/landlord-messages/<int:user_id>')
@login_required
def get_landlord_messages(user_id):
    """API endpoint to get messages for landlord"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'error': 'Database connection error'})
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT m.*, u.full_name as sender_name, u.profile_photo as sender_photo
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE (m.sender_id = %s AND m.receiver_id = %s) 
                   OR (m.sender_id = %s AND m.receiver_id = %s)
                ORDER BY m.created_at ASC
            """, (session['user_id'], user_id, user_id, session['user_id']))
            
            messages = cursor.fetchall()
            
            # Mark messages as read
            cursor.execute("""
                UPDATE messages SET is_read = TRUE 
                WHERE sender_id = %s AND receiver_id = %s AND is_read = FALSE
            """, (user_id, session['user_id']))
            connection.commit()
            
            # Format datetime for JSON
            for msg in messages:
                if msg.get('created_at'):
                    msg['created_at'] = msg['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return jsonify({'success': True, 'messages': messages})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        connection.close()