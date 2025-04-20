# Weather API Integration Instructions

You can integrate real weather data into your dashboard by configuring one of the following weather APIs:

## 1. OpenWeatherMap API Setup

1. **Sign up for an API key**:
   - Go to [OpenWeatherMap](https://openweathermap.org/)
   - Create a free account and get an API key
   - Free tier includes current weather data

2. **Configure environment variables on Render**:
   - Log in to Render.com
   - Go to your dashboard service
   - Click on "Environment"
   - Add the following environment variables:
     - `SENSOR_API_TYPE` = `openweathermap`
     - `SENSOR_API_KEY` = `your_openweathermap_api_key`
     - `SENSOR_API_LOCATION` = `London,UK` (or your desired location)

3. **In the dashboard**:
   - Select "API Data" in the data source dropdown

## 2. Visual Crossing Weather API Setup

1. **Sign up for an API key**:
   - Go to [Visual Crossing](https://www.visualcrossing.com/weather-api)
   - Create a free account and get an API key
   - Free tier includes historical weather data (ideal for this dashboard)

2. **Configure environment variables on Render**:
   - Add the following environment variables:
     - `SENSOR_API_TYPE` = `visualcrossing`
     - `SENSOR_API_KEY` = `your_visualcrossing_api_key`
     - `SENSOR_API_LOCATION` = `London,UK` (or your desired location)

3. **In the dashboard**:
   - Select "API Data" in the data source dropdown

## 3. ThingSpeak IoT Platform Setup (for your own sensors)

1. **Create a ThingSpeak channel**:
   - Go to [ThingSpeak](https://thingspeak.com/)
   - Create a free account
   - Create a new channel with three fields:
     - Field 1: Temperature
     - Field 2: Humidity
     - Field 3: Pressure
   - Note your Channel ID and Read API Key

2. **Configure environment variables on Render**:
   - Add the following environment variables:
     - `SENSOR_API_TYPE` = `thingspeak`
     - `SENSOR_API_KEY` = `your_thingspeak_read_api_key`
     - `THINGSPEAK_CHANNEL_ID` = `your_channel_id`

3. **In the dashboard**:
   - Select "API Data" in the data source dropdown

## Setting up your own weather station with ThingSpeak

If you want to build your own weather station to collect the data:

1. **Hardware needed**:
   - Arduino, ESP8266, or Raspberry Pi
   - BME280 or DHT22 sensor (measures temperature and humidity)
   - BMP280 sensor (measures pressure)

2. **Basic setup**:
   - Connect sensors to your microcontroller
   - Program it to read sensor values and send to ThingSpeak
   - Configure as described above

3. **Example Arduino code**:
   ```cpp
   #include <ThingSpeak.h>
   #include <WiFi.h>
   #include <BME280.h>

   // WiFi credentials
   const char* ssid = "your_wifi_ssid";
   const char* password = "your_wifi_password";

   // ThingSpeak settings
   unsigned long channelID = 12345;
   const char* writeAPIKey = "your_write_api_key";

   // BME280 sensor
   BME280 bme;

   void setup() {
     Serial.begin(115200);
     WiFi.begin(ssid, password);
     ThingSpeak.begin(client);
     bme.begin();
   }

   void loop() {
     float temperature = bme.readTemperature();
     float humidity = bme.readHumidity();
     float pressure = bme.readPressure() / 100.0F; // Convert to hPa

     // Send data to ThingSpeak
     ThingSpeak.setField(1, temperature);
     ThingSpeak.setField(2, humidity);
     ThingSpeak.setField(3, pressure);
     ThingSpeak.writeFields(channelID, writeAPIKey);

     delay(60000); // Wait 1 minute before next reading
   }
   ``` 