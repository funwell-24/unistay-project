#!/usr/bin/env python
"""
Script to create admin user
Run: python create_admin.py
"""

import bcrypt
import pymysql
from config import Config
import getpass

def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_admin():
    """Create admin user in the database"""
    
    print("\n🏠 UniStay - Admin Account Creator")
    print("=" * 40)
    
    # Get admin details
    full_name = input("Enter admin full name: ").strip()
    email = input("Enter admin email: ").strip()
    phone = input("Enter admin phone number: ").strip()
    password = getpass.getpass("Enter admin password: ").strip()
    confirm_password = getpass.getpass("Confirm password: ").strip()
    
    if password != confirm_password:
        print("\n❌ Passwords do not match!")
        return False
    
    # Connect to database
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Check if admin already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                print(f"\n❌ User with email {email} already exists!")
                return False
            
            # Hash password
            hashed_password = hash_password(password)
            
            # Insert admin user
            sql = """
                INSERT INTO users (full_name, email, phone, password_hash, user_type, is_verified, email_verified)
                VALUES (%s, %s, %s, %s, 'admin', TRUE, TRUE)
            """
            cursor.execute(sql, (full_name, email, phone, hashed_password))
            connection.commit()
            
            print(f"\n✅ Admin user created successfully!")
            print(f"   Name: {full_name}")
            print(f"   Email: {email}")
            print(f"   Type: Admin")
            return True
            
    except Exception as e:
        print(f"\n❌ Error creating admin: {e}")
        return False
    finally:
        connection.close()

if __name__ == '__main__':
    create_admin()