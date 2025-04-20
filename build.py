import os
import shutil

# Create public directory if it doesn't exist
if not os.path.exists('public'):
    os.makedirs('public')

# Copy static assets
if os.path.exists('assets'):
    if not os.path.exists('public/assets'):
        os.makedirs('public/assets')
    for file in os.listdir('assets'):
        shutil.copy2(f'assets/{file}', f'public/assets/{file}')

# Create a simple index.html with static content
with open('public/index.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Dash Sensor Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }
        h1 {
            color: #2c3e50;
        }
        .info {
            background-color: #f9f9f9;
            border-left: 4px solid #2c3e50;
            padding: 10px 20px;
            margin: 20px 0;
        }
        .button {
            display: inline-block;
            background-color: #2c3e50;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 4px;
            margin-top: 20px;
        }
        .button-group {
            margin-top: 30px;
        }
        .note {
            font-size: 0.9em;
            color: #666;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1>Dash Sensor Dashboard</h1>
    <p>This is the static hosting for the Dash Sensor Dashboard application.</p>
    
    <div class="info">
        <h2>Deployment Status</h2>
        <p>The static files have been successfully deployed to Firebase Hosting.</p>
        <p>This is your dashboard hosted at: <strong>dashweb-9ec83.web.app</strong></p>
    </div>
    
    <h2>Dashboard Features:</h2>
    <ul>
        <li>Real-time sensor data visualization</li>
        <li>AI prediction models</li>
        <li>Firebase integration for data storage</li>
        <li>Multiple visualization options</li>
        <li>User authentication</li>
    </ul>
    
    <p>Project ID: dashweb-9ec83</p>
    
    <div class="button-group">
        <a href="http://127.0.0.1:8050" class="button">Access Local Dashboard</a>
        <!-- Actual Render deployment URL -->
        <a href="https://dash-web-o40q.onrender.com" class="button" style="background-color: #FF4136;">Access Deployed Dashboard</a>
    </div>
    <p class="note">Your dashboard is now live on Render!</p>
</body>
</html>
    ''') 