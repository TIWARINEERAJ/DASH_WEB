"""
Test script to verify that app object is callable for Gunicorn
"""
import sys

try:
    # Import the app object from app.py
    from app import app
    
    # Check if app is callable
    if callable(app):
        print("SUCCESS: app object is callable and should work with Gunicorn")
        sys.exit(0)
    else:
        print(f"ERROR: app object is not callable: {type(app)}")
        sys.exit(1)
except Exception as e:
    print(f"ERROR: Could not import app: {str(e)}")
    sys.exit(1) 