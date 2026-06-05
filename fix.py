#!/usr/bin/env python
"""Script to update student.py dashboard route with primary_image"""

import os
import re

def update_student_dashboard():
    """Update the dashboard route in student.py to include primary_image"""
    
    student_py_path = 'blueprints/student.py'
    
    if not os.path.exists(student_py_path):
        print(f"❌ Error: {student_py_path} not found!")
        return False
    
    # Read the current file
    with open(student_py_path, 'r') as f:
        content = f.read()
    
    # Find the old query pattern
    old_query_pattern = r'cursor\.execute\("""\s*SELECT p\.\*, u\.full_name as landlord_name,\s*\(\s*SELECT AVG\(rating\) FROM reviews WHERE property_id = p\.id\s*\) as avg_rating\s*FROM properties p\s*JOIN users u ON p\.landlord_id = u\.id\s*WHERE p\.status = \'available\' AND p\.is_approved = TRUE\s*ORDER BY p\.created_at DESC\s*LIMIT 6\s*""")'
    
    # New query with primary_image
    new_query = '''cursor.execute("""
                SELECT p.*, u.full_name as landlord_name,
                       (SELECT AVG(rating) FROM reviews WHERE property_id = p.id) as avg_rating,
                       (SELECT media_url FROM property_media WHERE property_id = p.id AND is_primary = TRUE LIMIT 1) as primary_image
                FROM properties p
                JOIN users u ON p.landlord_id = u.id
                WHERE p.status = 'available' AND p.is_approved = TRUE
                ORDER BY p.created_at DESC
                LIMIT 6
            """)'''
    
    # Replace the query
    if 'primary_image' in content:
        print("✅ Dashboard route already has primary_image!")
        return True
    
    # Try to find and replace the specific section
    lines = content.split('\n')
    in_dashboard = False
    in_query = False
    query_lines = []
    start_idx = -1
    end_idx = -1
    
    for i, line in enumerate(lines):
        if '@student_bp.route('/dashboard')' in line:
            in_dashboard = True
        if in_dashboard and 'def dashboard' in line:
            start_idx = i
        if in_dashboard and 'cursor.execute(' in line and 'SELECT' in line:
            in_query = True
            query_lines = [i]
        if in_query and '""")' in line:
            end_idx = i
            break
        if in_query:
            query_lines.append(i)
    
    if start_idx != -1 and end_idx != -1:
        # Replace the old query with new one
        new_lines = []
        for i, line in enumerate(lines):
            if i == query_lines[0]:
                new_lines.append('            cursor.execute("""')
                new_lines.append('                SELECT p.*, u.full_name as landlord_name,')
                new_lines.append('                       (SELECT AVG(rating) FROM reviews WHERE property_id = p.id) as avg_rating,')
                new_lines.append('                       (SELECT media_url FROM property_media WHERE property_id = p.id AND is_primary = TRUE LIMIT 1) as primary_image')
                new_lines.append('                FROM properties p')
                new_lines.append('                JOIN users u ON p.landlord_id = u.id')
                new_lines.append('                WHERE p.status = \'available\' AND p.is_approved = TRUE')
                new_lines.append('                ORDER BY p.created_at DESC')
                new_lines.append('                LIMIT 6')
                new_lines.append('            """)')
                # Skip the old query lines
                for j in range(query_lines[0], end_idx + 1):
                    if j in query_lines and j != query_lines[0]:
                        continue
            elif i > end_idx or i < query_lines[0]:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
    
    # Write the updated content back
    with open(student_py_path, 'w') as f:
        f.write(content)
    
    print("✅ Updated student.py with primary_image query!")
    return True

def update_student_dashboard_simple():
    """Simpler version - direct string replacement"""
    
    student_py_path = 'blueprints/student.py'
    
    if not os.path.exists(student_py_path):
        print(f"❌ Error: {student_py_path} not found!")
        return False
    
    with open(student_py_path, 'r') as f:
        content = f.read()
    
    # Check if already updated
    if 'primary_image' in content and 'dashboard' in content:
        print("✅ Dashboard route already has primary_image!")
        return True
    
    # Find the dashboard section
    dashboard_start = content.find('@student_bp.route('/dashboard')')
    if dashboard_start == -1:
        print("❌ Could not find dashboard route!")
        return False
    
    # Find the query section
    query_start = content.find('cursor.execute("""', dashboard_start)
    if query_start == -1:
        print("❌ Could not find cursor.execute!")
        return False
    
    # Find the end of the query
    query_end = content.find('""")', query_start)
    if query_end == -1:
        print("❌ Could not find end of query!")
        return False
    
    # Extract the query
    old_query = content[query_start:query_end + 4]
    
    # Create new query with primary_image
    new_query = '''cursor.execute("""
                SELECT p.*, u.full_name as landlord_name,
                       (SELECT AVG(rating) FROM reviews WHERE property_id = p.id) as avg_rating,
                       (SELECT media_url FROM property_media WHERE property_id = p.id AND is_primary = TRUE LIMIT 1) as primary_image
                FROM properties p
                JOIN users u ON p.landlord_id = u.id
                WHERE p.status = 'available' AND p.is_approved = TRUE
                ORDER BY p.created_at DESC
                LIMIT 6
            """)'''
    
    # Replace the query
    content = content.replace(old_query, new_query)
    
    # Write back
    with open(student_py_path, 'w') as f:
        f.write(content)
    
    print("✅ Updated student.py with primary_image query!")
    return True

def show_current_dashboard_query():
    """Show the current dashboard query from student.py"""
    
    student_py_path = 'blueprints/student.py'
    
    if not os.path.exists(student_py_path):
        print(f"❌ Error: {student_py_path} not found!")
        return
    
    with open(student_py_path, 'r') as f:
        content = f.read()
    
    # Find the dashboard section
    dashboard_start = content.find('@student_bp.route('/dashboard')')
    if dashboard_start == -1:
        print("❌ Could not find dashboard route!")
        return
    
    # Extract the query section
    query_start = content.find('cursor.execute("""', dashboard_start)
    if query_start == -1:
        print("❌ Could not find cursor.execute!")
        return
    
    query_end = content.find('""")', query_start)
    if query_end == -1:
        print("❌ Could not find end of query!")
        return
    
    current_query = content[query_start:query_end + 4]
    
    print("\n" + "=" * 60)
    print("Current dashboard query in student.py:")
    print("=" * 60)
    print(current_query)
    print("=" * 60)
    
    if 'primary_image' in current_query:
        print("\n✅ primary_image is already included!")
    else:
        print("\n⚠️  primary_image is missing!")

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🏠 UniStay - Update Student Dashboard Query")
    print("=" * 60)
    
    print("\n1. Showing current query...")
    show_current_dashboard_query()
    
    print("\n2. Updating dashboard route...")
    update_student_dashboard_simple()
    
    print("\n3. Verifying update...")
    show_current_dashboard_query()
    
    print("\n✅ Done! Restart your server to see changes.")
    print("   Run: python run.py")