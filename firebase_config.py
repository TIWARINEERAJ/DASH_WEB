import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Firebase configuration
# In production, use environment variables or secure secret management
# For demo purposes, we'll attempt to load from a local file or create placeholder values

def initialize_firebase():
    """Initialize Firebase connection"""
    try:
        # Check if service account key file exists
        if os.path.exists('serviceAccountKey.json'):
            cred = credentials.Certificate('serviceAccountKey.json')
            firebase_admin.initialize_app(cred)
            return firestore.client()
        else:
            print("Firebase credentials not found. Using demo mode.")
            # For demo purposes only - no actual Firebase connection in this mode
            return None
    except Exception as e:
        print(f"Firebase initialization error: {e}")
        return None

def save_data_to_firebase(db, collection_name, data):
    """Save data to Firebase Firestore"""
    if db is None:
        print("Demo mode: Would save data to Firebase collection:", collection_name)
        return False
    
    try:
        # Convert dataframe to dict if needed
        if hasattr(data, 'to_dict'):
            data_dict = data.to_dict(orient='records')
        else:
            data_dict = data
            
        # Add data to collection
        collection_ref = db.collection(collection_name)
        
        for item in data_dict:
            # Add a timestamp field if not present
            if 'timestamp' not in item and 'date' in item:
                item['timestamp'] = item['date']
            collection_ref.add(item)
        
        return True
    except Exception as e:
        print(f"Error saving to Firebase: {e}")
        return False

def get_data_from_firebase(db, collection_name, limit=100):
    """Retrieve data from Firebase Firestore"""
    if db is None:
        print("Demo mode: Would retrieve data from Firebase collection:", collection_name)
        return None
    
    try:
        # Get data from collection with limit
        docs = db.collection(collection_name).limit(limit).get()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error retrieving from Firebase: {e}")
        return None 