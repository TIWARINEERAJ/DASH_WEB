"""
Simple test script to verify Firebase connection and write operations
"""
from firebase_config import initialize_firebase, save_data_to_firebase
from datetime import datetime

def test_firebase_connection():
    print("Testing Firebase connection...")
    
    # Initialize Firebase
    firebase_db = initialize_firebase()
    
    if firebase_db:
        print("Firebase initialized successfully!")
        
        # Create a simple test document
        test_data = [
            {
                "test_id": "test1",
                "message": "Test message from Dash Web App",
                "timestamp": datetime.now()
            }
        ]
        
        # Try to save to a test collection
        print("Attempting to save test data to Firebase...")
        success = save_data_to_firebase(firebase_db, "test_collection", test_data)
        
        if success:
            print("SUCCESS: Test data saved to Firebase!")
            print("Check your Firebase console for a collection named 'test_collection'")
        else:
            print("FAILED: Could not save test data to Firebase.")
            print("Check your permissions and network connection.")
    else:
        print("FAILED: Firebase initialization failed.")
        print("Make sure serviceAccountKey.json exists in the project root and has valid credentials.")
        print("The file should be in the same directory as this script.")

if __name__ == "__main__":
    test_firebase_connection() 