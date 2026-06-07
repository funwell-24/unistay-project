
from flask import Flask, render_template, session, flash, redirect, url_for, request
from config import config
import os
import pymysql
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Database connection function
def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            port=app.config['MYSQL_PORT'],   # ✅ REQUIRED FIX
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None
# Import blueprints
from blueprints.auth import auth_bp
from blueprints.student import student_bp
from blueprints.landlord import landlord_bp
from blueprints.admin import admin_bp
from blueprints.api import api_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(landlord_bp, url_prefix='/landlord')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(api_bp, url_prefix='/api')

# Context processor to inject user into templates
@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        connection = get_db_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
                    user = cursor.fetchone()
            finally:
                connection.close()
    return dict(current_user=user)


@app.route('/test')
def test_page():
    from datetime import datetime
    return render_template('test.html', now=datetime.now())

@app.route('/')
def index():
    """Home page with featured properties"""
    connection = get_db_connection()
    properties = []
    total_properties = 0
    total_landlords = 0
    total_students = 0
    
    if connection:
        try:
            with connection.cursor() as cursor:
                # Get featured/available properties
                cursor.execute("""
                    SELECT p.*, u.full_name as landlord_name,
                           (SELECT media_url FROM property_media WHERE property_id = p.id AND is_primary = TRUE LIMIT 1) as primary_image,
                           (SELECT AVG(rating) FROM reviews WHERE property_id = p.id AND is_approved = TRUE) as avg_rating,
                           (SELECT COUNT(*) FROM reviews WHERE property_id = p.id) as total_reviews
                    FROM properties p
                    JOIN users u ON p.landlord_id = u.id
                    WHERE p.status = 'available' AND p.is_approved = TRUE
                    ORDER BY p.created_at DESC
                    LIMIT 6
                """)
                properties = cursor.fetchall()
                
                # Get total available properties
                cursor.execute("SELECT COUNT(*) as count FROM properties WHERE status = 'available' AND is_approved = TRUE")
                result = cursor.fetchone()
                total_properties = result['count'] if result else 0
                
                # Get total verified landlords
                cursor.execute("SELECT COUNT(*) as count FROM users WHERE user_type = 'landlord' AND is_verified = TRUE")
                result = cursor.fetchone()
                total_landlords = result['count'] if result else 0
                
                # Get total students
                cursor.execute("SELECT COUNT(*) as count FROM users WHERE user_type = 'student'")
                result = cursor.fetchone()
                total_students = result['count'] if result else 0
        except Exception as e:
            print(f"Error fetching data: {e}")
        finally:
            connection.close()
    
    return render_template('index.html', 
                         properties=properties,
                         total_properties=total_properties,
                         total_landlords=total_landlords,
                         total_students=total_students)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204


@app.route('/search')
def search():
    """Search properties page"""
    connection = get_db_connection()
    properties = []
    
    if connection:
        try:
            with connection.cursor() as cursor:
                # Get filter parameters
                location = request.args.get('location', '')
                property_type = request.args.get('property_type', '')
                min_price = request.args.get('min_price', type=int)
                max_price = request.args.get('max_price', type=int)
                
                # Build query
                sql = """
                    SELECT p.*, u.full_name as landlord_name,
                           (SELECT AVG(rating) FROM reviews WHERE property_id = p.id AND is_approved = TRUE) as avg_rating
                    FROM properties p
                    JOIN users u ON p.landlord_id = u.id
                    WHERE p.status = 'available' AND p.is_approved = TRUE
                """
                params = []
                
                if location:
                    sql += " AND (p.location_area LIKE %s OR p.location_street LIKE %s)"
                    params.extend([f'%{location}%', f'%{location}%'])
                if property_type:
                    sql += " AND p.property_type = %s"
                    params.append(property_type)
                if min_price:
                    sql += " AND p.monthly_rent >= %s"
                    params.append(min_price)
                if max_price:
                    sql += " AND p.monthly_rent <= %s"
                    params.append(max_price)
                
                sql += " ORDER BY p.created_at DESC LIMIT 20"
                cursor.execute(sql, params)
                properties = cursor.fetchall()
        except Exception as e:
            print(f"Error searching properties: {e}")
        finally:
            connection.close()
    
    return render_template('student/properties.html', properties=properties)

@app.route('/property/<int:property_id>')
def property_detail(property_id):
    """Property details page"""
    connection = get_db_connection()
    property_data = None
    features = None
    images = []
    reviews = []
    landlord_profile_photo = None
    
    if connection:
        try:
            with connection.cursor() as cursor:
                # Get property details
                cursor.execute("""
                    SELECT p.*, u.full_name as landlord_name, u.phone as landlord_phone, 
                           u.email as landlord_email, u.id as landlord_id, u.profile_photo as landlord_profile_photo
                    FROM properties p
                    JOIN users u ON p.landlord_id = u.id
                    WHERE p.id = %s
                """, (property_id,))
                property_data = cursor.fetchone()
                
                if property_data:
                    # Get landlord profile photo
                    landlord_profile_photo = property_data.get('landlord_profile_photo')
                    
                    # Get property features
                    cursor.execute("SELECT * FROM property_features WHERE property_id = %s", (property_id,))
                    features = cursor.fetchone()
                    
                    # Get property images
                    cursor.execute("SELECT * FROM property_media WHERE property_id = %s ORDER BY is_primary DESC, sort_order", (property_id,))
                    images = cursor.fetchall()
                    
                    # Get reviews
                    cursor.execute("""
                        SELECT r.*, u.full_name
                        FROM reviews r
                        JOIN users u ON r.student_id = u.id
                        WHERE r.property_id = %s AND r.is_approved = TRUE
                        ORDER BY r.created_at DESC
                        LIMIT 10
                    """, (property_id,))
                    reviews = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching property details: {e}")
        finally:
            connection.close()
    
    if not property_data:
        flash('Property not found', 'danger')
        return redirect(url_for('index'))
    
    return render_template('student/property_detail.html', 
                         property=property_data,
                         features=features,
                         images=images,
                         reviews=reviews,
                         landlord_profile_photo=landlord_profile_photo)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
