import requests
import pandas as pd
from datetime import datetime, timedelta
import os

def fetch_visualcrossing_data(api_key, location="London,UK", days=30):
    """
    Fetch historical weather data from Visual Crossing Weather API
    
    This API actually provides historical data in the free tier,
    making it a good choice for your dashboard
    """
    # Calculate date range (last X days)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # API endpoint for historical data
    base_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{start_date}/{end_date}"
    
    # Parameters for the API request
    params = {
        "unitGroup": "metric",
        "key": api_key,
        "include": "days",
        "elements": "datetime,temp,humidity,pressure"
    }
    
    try:
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
            print(f"Error: API request failed with status code {response.status_code}")
            print(f"Message: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Replace with your actual API key
    API_KEY = "your_visualcrossing_api_key"
    
    # To use environment variable instead:
    # API_KEY = os.environ.get("VISUALCROSSING_API_KEY")
    
    # Fetch historical data for London
    weather_data = fetch_visualcrossing_data(API_KEY, location="London,UK", days=30)
    
    if weather_data is not None:
        # Display the data
        print("\nHistorical Weather Data:")
        print(weather_data)
        
        # Save to CSV
        weather_data.to_csv("visualcrossing_data.csv", index=False)
        print("\nData saved to visualcrossing_data.csv") 