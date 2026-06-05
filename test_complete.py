
#!/usr/bin/env python
"""Complete test for UniStay setup"""

import sys
import pymysql
from config import Config

print("=" * 50)
print("UniStay Configuration Test")
print("=" * 50)

# Test 1: Configuration loading
print("\n1. Testing Configuration Loading...")
print(f"   MYSQL_HOST: {Config.MYSQL_HOST}")
print(f"   MYSQL_USER: {Config.MYSQL_USER}")
print(f"   MYSQL_PASSWORD: {'*' * len(Config.MYSQL_PASSWORD)}")
print(f"   MYSQL_DB: {Config.MYSQL_DB}")
print(f"   MYSQL_PORT: {Config.MYSQL_PORT}")
print("   ✅ Configuration loaded successfully")

# Test 2: Database connection
print("\n2. Testing Database Connection...")
try:
    connection = pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )
    print("   ✅ Database connection successful!")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION() as version")
        result = cursor.fetchone()
        print(f"   MySQL Version: {result['version']}")
        
        # Fixed: Use a different alias instead of 'current_time'
        cursor.execute("SELECT NOW() as server_time")
        result = cursor.fetchone()
        print(f"   Server Time: {result['server_time']}")
        
        # Check if tables exist
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        if tables:
            print(f"   Tables found: {len(tables)}")
            for table in tables[:5]:  # Show first 5 tables
                table_name = list(table.values())[0]
                print(f"     - {table_name}")
        else:
            print("   ⚠️  No tables found. You need to import database.sql")
    
    connection.close()
    
except pymysql.err.OperationalError as e:
    print(f"   ❌ Database connection failed: {e}")
    print("\n   Troubleshooting:")
    print("   1. Check if MySQL is running: sudo systemctl status mysql")
    print("   2. Verify password in .env file")
    print("   3. Create database: mysql -u root -proot123 -e 'CREATE DATABASE unistay;'")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 3: File upload directory
print("\n3. Testing Upload Directory...")
import os
upload_dir = Config.UPLOAD_FOLDER
if os.path.exists(upload_dir):
    print(f"   ✅ Upload directory exists: {upload_dir}")
else:
    print(f"   ⚠️  Upload directory doesn't exist, creating...")
    os.makedirs(upload_dir, exist_ok=True)
    print(f"   ✅ Created upload directory: {upload_dir}")

print("\n" + "=" * 50)
print("✅ Database connection successful!")
print("=" * 50)

# Check if tables exist, if not suggest importing
if not tables:
    print("\n⚠️  Database has no tables. Please import the schema:")
    print("   mysql -u root -proot123 unistay < database/database.sql")
    print("\n   Or create tables manually from the SQL script provided.")
else:
    print("\n✅ Ready to run the application!")
    print("   Run: python run.py")
