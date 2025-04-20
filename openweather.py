import requests
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta
import time

class OpenWeatherDataManager:
    """Manager for fetching and processing weather data from OpenWeatherMap API"""
    
    def __init__(self, api_key=None, location="London", data_file="openweather_data.csv"):
        """Initialize with API key and location"""
        self.api_key = api_key or os.environ.get("OPENWEATHERMAP_API_KEY", "")
        self.location = location
        self.data_file = data_file
        
        # Base URLs for different OpenWeatherMap endpoints
        self.current_weather_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        
    def get_current_weather(self):
        """Get current weather data from OpenWeatherMap API"""
        if not self.api_key:
            print("API key not provided. Set it in the constructor or OPENWEATHERMAP_API_KEY environment variable.")
            return None
            
        # Parameters for the API request
        params = {
            "q": self.location,
            "appid": self.api_key,
            "units": "metric"  # For temperature in Celsius
        }
        
        try:
            # Make API request
            response = requests.get(self.current_weather_url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: API request failed with status code {response.status_code}")
                print(f"Message: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error fetching current weather data: {e}")
            return None
    
    def get_forecast(self, days=5):
        """Get 5-day forecast with 3-hour intervals (maximum for free tier)"""
        if not self.api_key:
            print("API key not provided. Set it in the constructor or OPENWEATHERMAP_API_KEY environment variable.")
            return None
            
        # Parameters for the API request
        params = {
            "q": self.location,
            "appid": self.api_key,
            "units": "metric",  # For temperature in Celsius
            "cnt": min(days * 8, 40)  # Maximum 40 timestamps (5 days with 3-hour intervals)
        }
        
        try:
            # Make API request
            response = requests.get(self.forecast_url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: Forecast API request failed with status code {response.status_code}")
                print(f"Message: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error fetching forecast data: {e}")
            return None
    
    def get_historical_data(self, days=7, simulated=True):
        """
        Get historical weather data
        
        Note: For free tier, this uses current weather and simulates historical data.
        For paid tier, you would implement the actual historical API endpoint.
        """
        if simulated:
            return self._simulate_historical_data(days)
        else:
            # This would implement the paid historical API
            print("Historical API requires OpenWeatherMap paid subscription. Using simulated data.")
            return self._simulate_historical_data(days)
    
    def _simulate_historical_data(self, days=7):
        """Generate simulated historical data based on current weather"""
        # Get current weather for base values
        current_data = self.get_current_weather()
        
        if not current_data:
            print("Failed to get current weather. Cannot simulate historical data.")
            return None
        
        # Extract base values
        current_temp = current_data['main']['temp']
        current_humidity = current_data['main']['humidity']
        current_pressure = current_data['main']['pressure']
        city_name = current_data['name']
        
        print(f"Current conditions in {city_name}:")
        print(f"Temperature: {current_temp}°C")
        print(f"Humidity: {current_humidity}%")
        print(f"Pressure: {current_pressure} hPa")
        
        # Create a more realistic dataset with seasonal patterns and trends
        dates = []
        temps = []
        humidities = []
        pressures = []
        
        # Generate simulated historical data based on current values
        np.random.seed(42)  # For reproducibility
        
        for i in range(days):
            # Work backwards from today
            date = datetime.now() - timedelta(days=i)
            dates.append(date)
            
            # Add some random variation with a touch of seasonality
            day_of_year = date.timetuple().tm_yday
            seasonal_factor = 2 * np.sin(2 * np.pi * day_of_year / 365)
            
            temp_variation = seasonal_factor + np.random.normal(0, 2)
            humidity_variation = -0.5 * seasonal_factor + np.random.normal(0, 5)
            pressure_variation = np.random.normal(0, 2)
            
            temps.append(current_temp + temp_variation)
            humidities.append(max(min(current_humidity + humidity_variation, 100), 0))
            pressures.append(current_pressure + pressure_variation)
        
        # Create a DataFrame with the data
        df = pd.DataFrame({
            'date': dates,
            'temperature': temps,
            'humidity': humidities,
            'pressure': pressures,
            'location': city_name
        })
        
        # Sort by date (oldest first)
        df = df.sort_values('date')
        
        return df
    
    def get_complete_weather_data(self, historical_days=30, include_forecast=True):
        """Get a complete dataset with historical and forecast data if available"""
        # Get historical data (simulated or real)
        historical_df = self.get_historical_data(days=historical_days)
        
        if historical_df is None:
            return None
            
        if include_forecast:
            # Get forecast data
            forecast_data = self.get_forecast()
            
            if forecast_data:
                forecast_list = forecast_data.get('list', [])
                city_name = forecast_data.get('city', {}).get('name', self.location)
                
                # Extract forecast data
                forecast_dates = []
                forecast_temps = []
                forecast_humidities = []
                forecast_pressures = []
                
                for item in forecast_list:
                    # Convert timestamp to datetime
                    timestamp = item.get('dt')
                    forecast_date = datetime.fromtimestamp(timestamp)
                    
                    main_data = item.get('main', {})
                    
                    forecast_dates.append(forecast_date)
                    forecast_temps.append(main_data.get('temp'))
                    forecast_humidities.append(main_data.get('humidity'))
                    forecast_pressures.append(main_data.get('pressure'))
                
                # Create forecast DataFrame
                forecast_df = pd.DataFrame({
                    'date': forecast_dates,
                    'temperature': forecast_temps,
                    'humidity': forecast_humidities,
                    'pressure': forecast_pressures,
                    'location': city_name,
                    'forecast': True  # Flag to indicate this is forecast data
                })
                
                # Add forecast flag to historical data
                historical_df['forecast'] = False
                
                # Combine historical and forecast data
                combined_df = pd.concat([historical_df, forecast_df], ignore_index=True)
                combined_df = combined_df.sort_values('date')
                
                return combined_df
        
        # If no forecast included or forecast failed, just return historical
        return historical_df
    
    def save_data_to_file(self, df, file_path=None):
        """Save weather data to a CSV file"""
        if df is None:
            print("No data to save")
            return False
            
        if file_path is None:
            file_path = self.data_file
            
        try:
            df.to_csv(file_path, index=False)
            print(f"Data saved to {file_path}")
            return True
        except Exception as e:
            print(f"Error saving data to file: {e}")
            return False

    def add_weather_metrics(self, df, temp_col='temperature', humidity_col='humidity'):
        """
        Add derived weather metrics to the DataFrame:
        - heat_index: Perceived temperature based on humidity and temperature
        - comfort_level: Classification of comfort based on temperature and humidity
        """
        if df is None or temp_col not in df.columns or humidity_col not in df.columns:
            print("DataFrame missing required columns")
            return df

        # Calculate heat index (perceived temperature)
        # Using a simplified formula based on US National Weather Service
        def heat_index(t, h):
            if t < 26:  # Only relevant for high temperatures
                return t
            
            # Constants for the heat index calculation
            c1 = -8.78469475556
            c2 = 1.61139411
            c3 = 2.33854883889
            c4 = -0.14611605
            c5 = -0.012308094
            c6 = -0.0164248277778
            c7 = 0.002211732
            c8 = 0.00072546
            c9 = -0.000003582
            
            hi = (c1 + c2*t + c3*h + c4*t*h + c5*t**2 + c6*h**2 + c7*t**2*h + c8*t*h**2 + c9*t**2*h**2)
            return round(hi, 1)
        
        # Define comfort levels based on temperature and humidity
        def comfort_level(t, h):
            if t < 15:
                return "Cold"
            elif t < 21:
                return "Cool"
            elif t < 26:
                if h < 60:
                    return "Comfortable"
                else:
                    return "Slightly Humid"
            elif t < 30:
                if h < 50:
                    return "Warm"
                elif h < 70:
                    return "Humid"
                else:
                    return "Very Humid"
            else:
                if h < 50:
                    return "Hot"
                else:
                    return "Very Hot"
        
        # Add new columns
        df['heat_index'] = df.apply(lambda row: heat_index(row[temp_col], row[humidity_col]), axis=1)
        df['comfort_level'] = df.apply(lambda row: comfort_level(row[temp_col], row[humidity_col]), axis=1)
        
        return df


# Example usage
if __name__ == "__main__":
    # Get API key from environment variable or replace with your actual key
    API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY", "your_openweathermap_api_key")
    
    # Initialize the OpenWeatherMap data manager
    weather_manager = OpenWeatherDataManager(api_key=API_KEY, location="London")
    
    # Get complete weather data (historical + forecast)
    weather_data = weather_manager.get_complete_weather_data(historical_days=30, include_forecast=True)
    
    if weather_data is not None:
        # Add derived weather metrics
        weather_data = weather_manager.add_weather_metrics(weather_data)
        
        # Display the first few rows
        print("\nWeather Data Sample:")
        print(weather_data.head())
        
        # Display basic statistics
        print("\nBasic Statistics:")
        print(weather_data[['temperature', 'humidity', 'pressure', 'heat_index']].describe())
        
        # Show distribution of comfort levels
        print("\nComfort Level Distribution:")
        print(weather_data['comfort_level'].value_counts())
        
        # Save to CSV
        weather_manager.save_data_to_file(weather_data, "openweather_enhanced_data.csv")
        print("\nData saved to openweather_enhanced_data.csv") 