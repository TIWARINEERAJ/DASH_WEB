"""
Module for interacting with Firebase Cloud Functions
"""
import requests
import json
import os
import random
from datetime import datetime

class FirebaseFunctions:
    """Interface for Firebase Cloud Functions"""
    
    def __init__(self):
        # Get the project ID from serviceAccountKey.json if available
        self.project_id = None
        self.region = "us-central1"  # Default region
        self.demo_mode = False
        
        try:
            if os.path.exists('serviceAccountKey.json'):
                with open('serviceAccountKey.json', 'r') as f:
                    service_account = json.load(f)
                    self.project_id = service_account.get('project_id')
            else:
                self.demo_mode = True
                print("ServiceAccountKey.json not found. Using demo mode for Cloud Functions.")
        except Exception as e:
            self.demo_mode = True
            print(f"Error getting project ID: {e}")
    
    def get_function_url(self, function_name):
        """Get the URL for a specific function"""
        if not self.project_id:
            return None
            
        return f"https://{self.region}-{self.project_id}.cloudfunctions.net/{function_name}"
    
    def get_stats(self):
        """Call the getStats function to retrieve latest statistics"""
        if self.demo_mode:
            print("Using demo data for get_stats()")
            return self._generate_demo_stats()
            
        function_url = self.get_function_url("getStats")
        
        if not function_url:
            print("Project ID not available. Using demo data for statistics.")
            return self._generate_demo_stats()
            
        try:
            response = requests.get(function_url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error calling getStats: {response.status_code} - {response.text}")
                return self._generate_demo_stats()
                
        except Exception as e:
            print(f"Error calling Cloud Function: {e}")
            return self._generate_demo_stats()
    
    def call_function(self, function_name, data=None):
        """Generic method to call any Firebase Cloud Function"""
        if self.demo_mode:
            print(f"Using demo data for {function_name}")
            return {"success": True, "demo": True, "message": "Demo mode active"}
            
        function_url = self.get_function_url(function_name)
        
        if not function_url:
            print("Project ID not available. Using demo mode for Cloud Functions.")
            return {"success": True, "demo": True, "message": "Demo mode active"}
            
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
            
    def _generate_demo_stats(self):
        """Generate demo statistics data for testing"""
        current_timestamp = {"_seconds": int(datetime.now().timestamp()), "_nanoseconds": 0}
        
        demo_stats = {
            "stats": [
                {
                    "type": "temperature_average",
                    "value": round(random.uniform(20, 25), 2),
                    "samples": random.randint(100, 500),
                    "timestamp": current_timestamp
                },
                {
                    "type": "humidity_average",
                    "value": round(random.uniform(40, 60), 2),
                    "samples": random.randint(100, 500),
                    "timestamp": current_timestamp
                },
                {
                    "type": "pressure_average",
                    "value": round(random.uniform(1000, 1020), 2),
                    "samples": random.randint(100, 500),
                    "timestamp": current_timestamp
                },
                {
                    "type": "prediction_accuracy",
                    "value": round(random.uniform(75, 95), 2),
                    "samples": random.randint(50, 200),
                    "timestamp": current_timestamp
                }
            ]
        }
        
        return demo_stats 