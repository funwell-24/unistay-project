
#!/usr/bin/env python
"""
UniStay Application Runner
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = ['MYSQL_HOST', 'MYSQL_USER', 'MYSQL_DB']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Warning: Missing environment variables:", ', '.join(missing_vars))
        print("Please check your .env file")
        return False
    return True

def main():
    """Main function to run the application"""
    
    # Get configuration from environment variables
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', '1').lower() in ['1', 'true', 'yes']
    
    # Print banner
    print("\n" + "=" * 60)
    print("🏠  UniStay Student Housing Platform")
    print("=" * 60)
    print(f"📍 Server URL: http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
    print(f"🔧 Debug Mode: {'ON' if debug else 'OFF'}")
    print(f"📁 Project Root: {os.path.dirname(os.path.abspath(__file__))}")
    print("=" * 60)
    
    # Check environment
    print("\n🔍 Checking environment...")
    if not check_environment():
        print("\n⚠️  Please create a .env file with the required configuration")
        print("Example .env file:")
        print("""
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=unistay
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=1
        """)
        sys.exit(1)
    
    # Import and run app
    try:
        from app import app
        print("✅ Flask app imported successfully")
        
        print("\n🚀 Starting UniStay server...")
        print("Press CTRL+C to stop the server\n")
        
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except ImportError as e:
        print(f"❌ Failed to import Flask app: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()