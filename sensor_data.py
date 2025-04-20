import pandas as pd
import numpy as np
import requests
import json
import os
from datetime import datetime, timedelta
import time

class SensorDataManager:
    """Manager for handling sensor data from various sources"""
    
    def __init__(self, data_source="simulated"):
        """Initialize with data source type"""
        self.data_source = data_source  # "simulated", "api", or "file"
        self.api_endpoint = os.environ.get("SENSOR_API_ENDPOINT", "")
        self.api_key = os.environ.get("SENSOR_API_KEY", "")
        self.data_file = os.environ.get("SENSOR_DATA_FILE", "sensor_data.csv")
        
    def get_sensor_data(self, days=100):
        """Get sensor data from the configured source"""
        if self.data_source == "simulated":
            return self._generate_simulated_data(days)
        elif self.data_source == "api":
            return self._fetch_api_data(days)
        elif self.data_source == "file":
            return self._read_file_data()
        else:
            # Default to simulated data if unknown source
            return self._generate_simulated_data(days)
            
    def _generate_simulated_data(self, days=100):
        """Generate simulated sensor data"""
        # Create a more realistic dataset with seasonal patterns and trends
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Create seasonal components (annual cycle)
        day_of_year = np.array([d.dayofyear for d in dates])
        annual_cycle = 10 * np.sin(2 * np.pi * day_of_year / 365)
        
        # Random seed for reproducibility
        np.random.seed(42)
        
        # Base values with seasonal variations and some noise
        temperature = 25 + annual_cycle + np.random.normal(0, 3, days)
        humidity = 60 + (-5 * annual_cycle) + np.random.normal(0, 5, days)
        pressure = 1013 + np.random.normal(0, 3, days)
        
        # Add some correlation between variables
        humidity += 0.2 * temperature
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure,
        })
        
        # Add a small number of anomalies (10% probability)
        anomaly_mask = np.random.random(days) < 0.1
        df.loc[anomaly_mask, 'temperature'] += np.random.choice([-10, 10], size=sum(anomaly_mask))
        
        return df
    
    def _fetch_api_data(self, days=100):
        """Fetch data from an API endpoint"""
        if not self.api_endpoint or not self.api_key:
            print("API endpoint or key not configured. Using simulated data.")
            return self._generate_simulated_data(days)
            
        try:
            # Calculate the start date for the request
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            # Make the API request
            params = {
                "api_key": self.api_key,
                "start_date": start_date,
                "end_date": end_date,
                "metrics": "temperature,humidity,pressure"
            }
            
            response = requests.get(self.api_endpoint, params=params)
            
            if response.status_code == 200:
                # Assume the API returns JSON with a data array
                data = response.json().get("data", [])
                
                if data:
                    # Convert to DataFrame
                    df = pd.DataFrame(data)
                    
                    # Ensure date column is datetime
                    df['date'] = pd.to_datetime(df['date'])
                    
                    return df
                    
            # If we get here, the API request failed or returned no data
            print(f"API request failed with status {response.status_code}. Using simulated data.")
            return self._generate_simulated_data(days)
            
        except Exception as e:
            print(f"Error fetching API data: {e}. Using simulated data.")
            return self._generate_simulated_data(days)
    
    def _read_file_data(self):
        """Read sensor data from a file"""
        try:
            if os.path.exists(self.data_file):
                df = pd.read_csv(self.data_file)
                
                # Ensure date column is datetime
                df['date'] = pd.to_datetime(df['date'])
                
                return df
            else:
                print(f"Data file {self.data_file} not found. Using simulated data.")
                return self._generate_simulated_data()
                
        except Exception as e:
            print(f"Error reading file data: {e}. Using simulated data.")
            return self._generate_simulated_data()
    
    def save_data_to_file(self, df, file_path=None):
        """Save sensor data to a CSV file"""
        if file_path is None:
            file_path = self.data_file
            
        try:
            df.to_csv(file_path, index=False)
            print(f"Data saved to {file_path}")
            return True
        except Exception as e:
            print(f"Error saving data to file: {e}")
            return False 