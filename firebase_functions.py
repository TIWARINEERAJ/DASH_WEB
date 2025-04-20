"""
Module for interacting with Firebase Cloud Functions
"""
import requests
import json
import os

class FirebaseFunctions:
    """Interface for Firebase Cloud Functions"""
    
    def __init__(self):
        # Get the project ID from serviceAccountKey.json if available
        self.project_id = None
        self.region = "us-central1"  # Default region
        
        try:
            if os.path.exists('serviceAccountKey.json'):
                with open('serviceAccountKey.json', 'r') as f:
                    service_account = json.load(f)
                    self.project_id = service_account.get('project_id')
        except Exception as e:
            print(f"Error getting project ID: {e}")
    
    def get_function_url(self, function_name):
        """Get the URL for a specific function"""
        if not self.project_id:
            return None
            
        return f"https://{self.region}-{self.project_id}.cloudfunctions.net/{function_name}"
    
    def get_stats(self):
        """Call the getStats function to retrieve latest statistics"""
        function_url = self.get_function_url("getStats")
        
        if not function_url:
            print("Project ID not available. Cannot call Cloud Function.")
            return None
            
        try:
            response = requests.get(function_url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error calling getStats: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error calling Cloud Function: {e}")
            return None
    
    def call_function(self, function_name, data=None):
        """Generic method to call any Firebase Cloud Function"""
        function_url = self.get_function_url(function_name)
        
        if not function_url:
            print("Project ID not available. Cannot call Cloud Function.")
            return None
            
        try:
            if data:
                response = requests.post(function_url, json=data, timeout=10)
            else:
                response = requests.get(function_url, timeout=10)
                
            if response.status_code in (200, 201, 204):
                try:
                    return response.json()
                except:
                    return {"success": True, "status_code": response.status_code}
            else:
                print(f"Error calling {function_name}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error calling Cloud Function: {e}")
            return None 