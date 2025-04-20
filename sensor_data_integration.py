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
        self.data_source = data_source  # "simulated", "api", "file", or "firebase"
        
        # API configuration
        self.api_type = os.environ.get("SENSOR_API_TYPE", "openweathermap")
        self.api_key = os.environ.get("SENSOR_API_KEY", "")
        self.api_location = os.environ.get("SENSOR_API_LOCATION", "London,UK")
        
        # File configuration
        self.data_file = os.environ.get("SENSOR_DATA_FILE", "sensor_data.csv")
        
    def get_sensor_data(self, days=100):
        """Get sensor data from the configured source"""
        if self.data_source == "simulated":
            return self._generate_simulated_data(days)
        elif self.data_source == "api":
            return self._fetch_api_data(days)
        elif self.data_source == "file":
            return self._read_file_data()
        elif self.data_source == "firebase":
            # This would be handled by your Firebase code
            # For now, fall back to simulated data
            print("Firebase data source selected, but returning simulated data")
            return self._generate_simulated_data(days)
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
        if not self.api_key:
            print("API key not configured. Using simulated data.")
            return self._generate_simulated_data(days)
            
        try:
            # Select the appropriate API handler based on the configuration
            if self.api_type.lower() == "openweathermap":
                return self._fetch_openweathermap_data(days)
            elif self.api_type.lower() == "visualcrossing":
                return self._fetch_visualcrossing_data(days)
            elif self.api_type.lower() == "thingspeak":
                return self._fetch_thingspeak_data(days)
            else:
                print(f"Unknown API type: {self.api_type}. Using simulated data.")
                return self._generate_simulated_data(days)
                
        except Exception as e:
            print(f"Error fetching API data: {e}. Using simulated data.")
            return self._generate_simulated_data(days)
    
    def _fetch_openweathermap_data(self, days=100):
        """Fetch data from OpenWeatherMap API"""
        location = self.api_location or "London"
        
        # For current weather (free tier)
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        
        # Parameters for the API request
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric"  # For temperature in Celsius
        }
        
        # Make API request
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant data
            current_temp = data['main']['temp']
            current_humidity = data['main']['humidity']
            current_pressure = data['main']['pressure']
            
            print(f"Current conditions in {location}:")
            print(f"Temperature: {current_temp}°C")
            print(f"Humidity: {current_humidity}%")
            print(f"Pressure: {current_pressure} hPa")
            
            # For demo purposes, create a series of historical data
            # In a production app, you'd use the historical API (paid tier)
            
            dates = []
            temps = []
            humidities = []
            pressures = []
            
            for i in range(days):
                # Work backwards from today
                date = datetime.now() - timedelta(days=i)
                dates.append(date)
                
                # Add some random variation to create simulated historical data
                import random
                temp_variation = random.uniform(-3, 3)
                humidity_variation = random.uniform(-10, 10)
                pressure_variation = random.uniform(-5, 5)
                
                temps.append(current_temp + temp_variation)
                humidities.append(max(min(current_humidity + humidity_variation, 100), 0))
                pressures.append(current_pressure + pressure_variation)
            
            # Create a DataFrame with the data
            df = pd.DataFrame({
                'date': dates,
                'temperature': temps,
                'humidity': humidities,
                'pressure': pressures
            })
            
            # Sort by date (oldest first)
            df = df.sort_values('date')
            
            return df
        else:
            print(f"Error calling OpenWeatherMap API: {response.status_code} - {response.text}")
            return self._generate_simulated_data(days)
            
    def _fetch_visualcrossing_data(self, days=100):
        """Fetch historical weather data from Visual Crossing Weather API"""
        location = self.api_location or "London,UK"
        
        # Calculate date range
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # API endpoint for historical data
        base_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{start_date}/{end_date}"
        
        # Parameters for the API request
        params = {
            "unitGroup": "metric",
            "key": self.api_key,
            "include": "days",
            "elements": "datetime,temp,humidity,pressure"
        }
        
        # Make API request
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract daily data
            days_data = data.get('days', [])
            
            # Create lists to hold the data
            dates = []
            temps = []
            humidities = []
            pressures = []
            
            for day in days_data:
                dates.append(day.get('datetime'))
                temps.append(day.get('temp'))
                humidities.append(day.get('humidity'))
                pressures.append(day.get('pressure', 1013))  # Default pressure if missing
            
            # Create a DataFrame
            df = pd.DataFrame({
                'date': pd.to_datetime(dates),
                'temperature': temps,
                'humidity': humidities,
                'pressure': pressures
            })
            
            return df
        else:
            print(f"Error calling Visual Crossing API: {response.status_code} - {response.text}")
            return self._generate_simulated_data(days)
    
    def _fetch_thingspeak_data(self, days=100):
        """Fetch sensor data from ThingSpeak IoT platform"""
        # ThingSpeak requires channel ID, typically stored in the location field or as separate env var
        channel_parts = self.api_location.split(",") if self.api_location else []
        channel_id = channel_parts[0] if channel_parts else os.environ.get("THINGSPEAK_CHANNEL_ID", "")
        
        if not channel_id:
            print("ThingSpeak channel ID not found. Using simulated data.")
            return self._generate_simulated_data(days)
        
        # Calculate start time (in seconds from now)
        start_time = int((datetime.now() - timedelta(days=days)).timestamp())
        
        # API endpoint
        base_url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json"
        
        # Parameters
        params = {
            "api_key": self.api_key,
            "start": start_time,
            "results": 8000  # Maximum results per request
        }
        
        # Make API request
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract feeds data
            feeds = data.get('feeds', [])
            
            if not feeds:
                print("No data found for the specified time period")
                return self._generate_simulated_data(days)
                
            # Create a DataFrame
            df = pd.DataFrame(feeds)
            
            # Rename columns to match your expected format
            column_mapping = {
                'created_at': 'date',
                'field1': 'temperature',  # Assuming field1 is temperature
                'field2': 'humidity',     # Assuming field2 is humidity
                'field3': 'pressure'      # Assuming field3 is pressure
            }
            
            # Rename columns that exist
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df = df.rename(columns={old_col: new_col})
            
            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])
            
            # Convert numeric columns to float
            for col in ['temperature', 'humidity', 'pressure']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Drop unnecessary columns (entry_id and other fields)
            essential_columns = ['date', 'temperature', 'humidity', 'pressure']
            df = df[[col for col in essential_columns if col in df.columns]]
            
            return df
        else:
            print(f"Error calling ThingSpeak API: {response.status_code} - {response.text}")
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