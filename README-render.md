# Deploying the Dash Sensor Dashboard to Render

## Option 1: One-Click Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/TIWARINEERAJ/DASH_WEB)

## Option 2: Manual Deployment

1. Create a new account on [Render](https://render.com/) if you don't have one
2. From the Render dashboard, click "New +" and select "Web Service"
3. Connect your GitHub repository (or select "Public Git Repository" and enter the URL)
4. Configure the service:
   - **Name**: dash-sensor-dashboard (or your preferred name)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:server`
5. Click "Create Web Service"

## After Deployment

Once deployed, Render will provide you with a URL like:
```
https://dash-sensor-dashboard.onrender.com
```

Update your Firebase landing page to point to this URL:

1. Edit `build.py` to update the "Access Local Dashboard" button URL
2. Run `python build.py`
3. Run `firebase deploy --only hosting`

## Environment Variables

If you need to set environment variables (like for Firebase credentials), you can do so in the Render dashboard:

1. Go to your web service in the Render dashboard
2. Click on "Environment"
3. Add your environment variables (like `FIREBASE_PROJECT_ID`, etc.)

## Continuous Deployment

Render automatically deploys your app when you push changes to your connected repository. 