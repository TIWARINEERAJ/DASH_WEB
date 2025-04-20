import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import time
from datetime import datetime
import shutil

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

def save_data_to_firebase(db, collection_name, data, max_retries=3, batch_size=50):
    """Save data to Firebase Firestore with improved error handling and batching"""
    if db is None:
        print("Demo mode: Would save data to Firebase collection:", collection_name)
        return False
    
    try:
        # Convert dataframe to dict if needed
        if hasattr(data, 'to_dict'):
            data_dict = data.to_dict(orient='records')
        else:
            data_dict = data
            
        if not data_dict:
            print(f"No data to save to {collection_name}")
            return True
            
        print(f"Attempting to save {len(data_dict)} items to {collection_name}")
        
        # Process in batches to avoid timeouts and rate limits
        for retry in range(max_retries):
            try:
                # Use batched writes for better performance
                total_batches = (len(data_dict) + batch_size - 1) // batch_size
                
                for batch_num in range(total_batches):
                    start_idx = batch_num * batch_size
                    end_idx = min(start_idx + batch_size, len(data_dict))
                    batch_items = data_dict[start_idx:end_idx]
                    
                    # Create a batch
                    batch = db.batch()
                    
                    # Add each item to the batch
                    for item in batch_items:
                        # Add a timestamp field if not present
                        if 'timestamp' not in item and 'date' in item:
                            item['timestamp'] = item['date']
                            
                        # Create a reference to a new document
                        doc_ref = db.collection(collection_name).document()
                        batch.set(doc_ref, item)
                    
                    # Commit the batch
                    batch.commit()
                    print(f"Saved batch {batch_num+1}/{total_batches} to {collection_name}")
                    
                    # Small delay to avoid rate limiting
                    if batch_num < total_batches - 1:
                        time.sleep(0.5)
                
                print(f"Successfully saved all data to {collection_name}")
                return True
                
            except Exception as e:
                print(f"Error on attempt {retry+1}: {e}")
                if retry < max_retries - 1:
                    wait_time = (retry + 1) * 2  # Exponential backoff
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"Failed after {max_retries} attempts")
                    return False
                    
    except Exception as e:
        print(f"Error preparing data for Firebase: {e}")
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

# Create public directory if it doesn't exist
if not os.path.exists('public'):
    os.makedirs('public')

# Copy static assets
if os.path.exists('assets'):
    if not os.path.exists('public/assets'):
        os.makedirs('public/assets')
    for file in os.listdir('assets'):
        shutil.copy2(f'assets/{file}', f'public/assets/{file}')

# Create a simple index.html that redirects to the app
with open('public/index.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Dash Sensor Dashboard</title>
    <meta http-equiv="refresh" content="0;URL='https://your-project-id.web.app/_dash-routes/'" />
</head>
<body>
    <p>Redirecting to the dashboard...</p>
</body>
</html>
    '''.replace('your-project-id', 'dashweb-9ec83')) 