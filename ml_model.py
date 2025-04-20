import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

class PredictionModel:
    """Simple prediction model for sensor data"""
    
    def __init__(self):
        self.models = {}
        self.metrics = ['temperature', 'humidity', 'pressure']
        
    def preprocess_data(self, df):
        """Preprocess the data for model training/prediction"""
        # Create features based on date
        df = df.copy()
        
        if 'date' in df.columns:
            df['day_of_year'] = df['date'].dt.dayofyear
            df['month'] = df['date'].dt.month
            df['day'] = df['date'].dt.day
            
            # Create lag features (previous day values)
            for metric in self.metrics:
                if metric in df.columns:
                    df[f'{metric}_lag1'] = df[metric].shift(1)
                    
            # Drop NaN values from lag creation
            df = df.dropna()
            
        return df
    
    def train_models(self, df):
        """Train prediction models for each metric"""
        processed_df = self.preprocess_data(df)
        
        for metric in self.metrics:
            if metric in processed_df.columns:
                # Features: date-based features and lag values
                X = processed_df[['day_of_year', 'month', 'day', f'{metric}_lag1']]
                y = processed_df[metric]
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                # Create and train model
                model = Pipeline([
                    ('scaler', StandardScaler()),
                    ('regressor', LinearRegression())
                ])
                
                model.fit(X_train, y_train)
                self.models[metric] = model
                
                # Evaluate
                score = model.score(X_test, y_test)
                print(f"Model for {metric} trained with R² score: {score:.4f}")
    
    def predict_next_values(self, df, days_ahead=7):
        """Predict values for the next n days"""
        if not self.models:
            print("Models not trained yet")
            return None
            
        # Use the last available data for prediction
        processed_df = self.preprocess_data(df)
        
        if processed_df.empty:
            return None
            
        last_date = df['date'].max()
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days_ahead)
        
        # Create prediction dataframe
        future_df = pd.DataFrame({'date': future_dates})
        future_df['day_of_year'] = future_df['date'].dt.dayofyear
        future_df['month'] = future_df['date'].dt.month
        future_df['day'] = future_df['date'].dt.day
        
        # Initialize with last known values
        for metric in self.metrics:
            if metric in processed_df.columns and metric in self.models:
                future_df[f'{metric}_lag1'] = processed_df[metric].iloc[-1]
                
                # Predict each day incrementally
                for i in range(len(future_df)):
                    # Prepare features for prediction
                    features = future_df.iloc[i:i+1][['day_of_year', 'month', 'day', f'{metric}_lag1']]
                    
                    # Predict
                    prediction = self.models[metric].predict(features)[0]
                    future_df.loc[i, metric] = prediction
                    
                    # Update lag for next prediction if not last row
                    if i < len(future_df) - 1:
                        future_df.loc[i+1, f'{metric}_lag1'] = prediction
        
        # Keep only relevant columns
        result_df = future_df[['date'] + [m for m in self.metrics if m in future_df.columns]]
        return result_df 