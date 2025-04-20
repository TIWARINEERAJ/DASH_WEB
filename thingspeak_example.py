import requests
import pandas as pd
from datetime import datetime, timedelta
import json

def fetch_thingspeak_data(channel_id, read_api_key, days=30):
    """
    Fetch sensor data from ThingSpeak IoT platform
    
    ThingSpeak is great if you want to connect your own sensors
    (like Arduino, ESP8266, Raspberry Pi) to your dashboard
    """
    # Calculate start time (in seconds from now)
    start_time = int((datetime.now() - timedelta(days=days)).timestamp())
    
    # API endpoint
    base_url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json"
    
    # Parameters
    params = {
        "api_key": read_api_key,
        "start": start_time,
        "results": 8000  # Maximum results per request
    }
    
    try:
        # Make API request
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract feeds data
            feeds = data.get('feeds', [])
            
            if not feeds:
                print("No data found for the specified time period")
                return None
                
            # Create a DataFrame
            df = pd.DataFrame(feeds)
            
            # Rename columns to match your expected format
            # Note: ThingSpeak uses field1, field2, etc. for data
            # You need to map these to your temperature, humidity, pressure fields
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
            print(f"Error: API request failed with status code {response.status_code}")
            print(f"Message: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Replace with your actual ThingSpeak channel ID and API key
    CHANNEL_ID = "12345"  # Your ThingSpeak channel ID
    READ_API_KEY = "your_thingspeak_read_api_key"
    
    # Fetch data
    sensor_data = fetch_thingspeak_data(CHANNEL_ID, READ_API_KEY, days=30)
    
    if sensor_data is not None:
        # Display the first few rows
        print("\nSensor Data Sample:")
        print(sensor_data.head())
        
        # Save to CSV
        sensor_data.to_csv("thingspeak_data.csv", index=False)
        print("\nData saved to thingspeak_data.csv") 