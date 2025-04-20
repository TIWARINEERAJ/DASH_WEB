# Dash Interactive Visualization Dashboard

A comprehensive Dash web application that demonstrates interactive data visualization with sensor data, AI predictions, Firebase integration, and multiple visualization types.

## Deployment URLs

- Firebase (Static Landing Page): https://dashweb-9ec83.web.app
- Render (Full Application): https://dash-web-o40q.onrender.com

## Features

### 1. Real Sensor Data Integration
- Simulated sensor data with realistic patterns
- API connector for real sensor data
- File-based data loading
- Automatic fallback to simulation when other sources unavailable

### 2. AI Prediction Feedback Loop
- Machine learning models to predict future values
- Linear regression with preprocessing pipeline
- Visualization of predictions alongside actual data
- Automatic model retraining when new data arrives

### 3. Firebase Integration
- Firestore database connection
- Save and retrieve sensor data
- Store AI predictions
- Cloud Functions for server-side processing
- Graceful fallback when Firebase unavailable

### 4. Advanced Visualizations
- Interactive time series visualization
- Multi-metric comparison with dual y-axis
- Correlation heatmap
- Statistical distribution analysis
- Summary statistics table

### Firebase Web SDK Integration (Optional)
1. Register your web app in the Firebase Console
2. Copy your Firebase configuration from the Firebase Console
3. Update the `assets/firebase-config.js` file with your configuration
4. Enable Authentication in the Firebase Console (Email/Password provider)
5. Restart your app and use the Authentication tab for user management

## Installation

1. Clone this repository
2. Install the required packages:

```
pip install -r requirements.txt
```

## Configuration

### Firebase Setup (Optional)
1. Create a Firebase project at https://console.firebase.google.com/
2. Generate a service account key and save as `serviceAccountKey.json` in the project root
3. The app will automatically detect and use Firebase if configured

### Firebase Cloud Functions Setup (Optional)
1. Install Node.js and Firebase CLI
   ```
   npm install -g firebase-tools
   ```

2. Initialize and deploy Firebase Functions
   ```
   firebase login
   firebase init functions
   ```

3. Copy the Cloud Functions code provided in the `functions/index.js` file
4. Deploy the functions
   ```
   firebase deploy --only functions
   ```

### Sensor API Setup (Optional)
1. Set environment variables for API connection:
   - `SENSOR_API_ENDPOINT`: URL of your sensor data API
   - `SENSOR_API_KEY`: API key for authentication
   - `DATA_SOURCE`: Set to "api" to use API data source

## Running the Application

Run the application with:

```
python app.py
```

Then open your browser and navigate to http://127.0.0.1:8050/

## Project Structure

- `app.py`: Main Dash application
- `ml_model.py`: Machine learning module for predictions
- `sensor_data.py`: Sensor data integration module
- `firebase_config.py`: Firebase database integration
- `firebase_functions.py`: Interface for Firebase Cloud Functions
- `assets/style.css`: Custom styling
- `functions/index.js`: Firebase Cloud Functions code

## Deployment

For production deployment, you can use services like Heroku, AWS, or Azure. The app includes a `server` variable that's required for production deployment on most platforms. 

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050) 