import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time

def fetch_openweathermap_data(api_key, city="London", days=7):
    """
    Fetch current weather data from OpenWeatherMap API
    and simulate historical data by creating multiple entries
    """
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    # Parameters for the API request
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"  # For temperature in Celsius
    }
    
    try:
        # Make API request
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant data
            current_temp = data['main']['temp']
            current_humidity = data['main']['humidity']
            current_pressure = data['main']['pressure']
            
            print(f"Current conditions in {city}:")
            print(f"Temperature: {current_temp}°C")
            print(f"Humidity: {current_humidity}%")
            print(f"Pressure: {current_pressure} hPa")
            
            # For demo purposes, create a series of historical data
            # Note: Free OpenWeatherMap API doesn't provide historical data
            # This section simulates what historical data might look like
            
            dates = []
            temps = []
            humidities = []
            pressures = []
            
            # Generate simulated historical data based on current values
            for i in range(days):
                # Work backwards from today
                date = datetime.now() - timedelta(days=i)
                dates.append(date)
                
                # Add some random variation to create fake historical data
                # In a real app, you'd use the historical API endpoints if available
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
            print(f"Error: API request failed with status code {response.status_code}")
            print(f"Message: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Replace with your actual API key
    API_KEY = "your_openweathermap_api_key"
    
    # To use environment variable instead:
    # API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")
    
    # Fetch data for London
    weather_data = fetch_openweathermap_data(API_KEY, city="London", days=30)
    
    if weather_data is not None:
        # Display the first few rows
        print("\nHistorical Data Sample:")
        print(weather_data.head())
        
        # Save to CSV
        weather_data.to_csv("openweathermap_data.csv", index=False)
        print("\nData saved to openweathermap_data.csv") 