import dash
from dash import dcc, html, callback, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Import our modules
from sensor_data import SensorDataManager
from ml_model import PredictionModel
from firebase_config import initialize_firebase, save_data_to_firebase, get_data_from_firebase
from firebase_functions import FirebaseFunctions

# Initialize components
sensor_manager = SensorDataManager(data_source=os.environ.get("DATA_SOURCE", "simulated"))
prediction_model = PredictionModel()
firebase_db = initialize_firebase()

# Initialize Firebase Functions
firebase_functions = FirebaseFunctions()

# Get sensor data
df = sensor_manager.get_sensor_data(days=100)

# Train ML models on the data
prediction_model.train_models(df)

# Make predictions
prediction_df = prediction_model.predict_next_values(df, days_ahead=7)

# Try to save to Firebase (if configured)
if firebase_db:
    print("Attempting to save sensor data to Firebase...")
    sensor_success = save_data_to_firebase(firebase_db, "sensor_data", df)
    print(f"Save sensor data to Firebase {'successful' if sensor_success else 'failed'}")
    
    print("Attempting to save predictions to Firebase...")
    pred_success = save_data_to_firebase(firebase_db, "predictions", prediction_df)
    print(f"Save predictions to Firebase {'successful' if pred_success else 'failed'}")
else:
    print("Firebase database connection not established. Check serviceAccountKey.json")

# Initialize the Dash app
app = dash.Dash(
    __name__, 
    title="Interactive Visualization Dashboard",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
    external_scripts=[
        "https://www.gstatic.com/firebasejs/9.22.0/firebase-app-compat.js",
        "https://www.gstatic.com/firebasejs/9.22.0/firebase-firestore-compat.js",
        "https://www.gstatic.com/firebasejs/9.22.0/firebase-auth-compat.js",
        "https://www.gstatic.com/firebasejs/9.22.0/firebase-analytics-compat.js"
    ]
)

# This is the server variable needed for Render
server = app.server

# For compatibility with both app:app and app:server in Gunicorn
application = app.server

# Define metric information
METRICS = {
    'temperature': {'label': 'Temperature (°C)', 'color': '#FF4136'},
    'humidity': {'label': 'Humidity (%)', 'color': '#0074D9'},
    'pressure': {'label': 'Pressure (hPa)', 'color': '#2ECC40'}
}

# Define the app layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Sensor Data Dashboard", style={'textAlign': 'center'}),
        html.P("Interactive visualization with real-time sensor data and AI predictions", 
               style={'textAlign': 'center'}),
    ], style={'padding': '2rem 0'}),
    
    # Tabs for different views
    dcc.Tabs([
        # Main dashboard tab
        dcc.Tab(label="Dashboard", children=[
            # Data Source Selection
            html.Div([
                html.Div([
                    html.Label("Data Source:"),
                    dcc.RadioItems(
                        id='data-source-selector',
                        options=[
                            {'label': 'Simulated Data', 'value': 'simulated'},
                            {'label': 'API Data (if configured)', 'value': 'api'},
                            {'label': 'File Data (if available)', 'value': 'file'},
                            {'label': 'Firebase Data (if configured)', 'value': 'firebase'}
                        ],
                        value='simulated',
                        labelStyle={'display': 'inline-block', 'marginRight': '10px'}
                    ),
                ], style={'margin': '0 auto', 'maxWidth': '600px', 'textAlign': 'center'}),
            ], style={'margin': '1rem 0'}),
            
            # Main content
            html.Div([
                # Left Side: Controls
                html.Div([
                    # Main metric selection
                    html.Div([
                        html.Label("Select Primary Metric:"),
                        dcc.Dropdown(
                            id='metric-selector',
                            options=[
                                {'label': METRICS[m]['label'], 'value': m}
                                for m in METRICS
                            ],
                            value='temperature',
                            clearable=False
                        ),
                    ], style={'marginBottom': '20px'}),
                    
                    # Date range selector
                    html.Div([
                        html.Label("Date Range:"),
                        dcc.DatePickerRange(
                            id='date-range',
                            min_date_allowed=df['date'].min(),
                            max_date_allowed=df['date'].max(),
                            start_date=df['date'].max() - timedelta(days=30),
                            end_date=df['date'].max(),
                        ),
                    ], style={'marginBottom': '20px'}),
                    
                    # Show predictions toggle
                    html.Div([
                        html.Label("Show AI Predictions:"),
                        dcc.RadioItems(
                            id='show-predictions',
                            options=[
                                {'label': 'Yes', 'value': 'yes'},
                                {'label': 'No', 'value': 'no'}
                            ],
                            value='yes',
                            labelStyle={'display': 'inline-block', 'marginRight': '10px'}
                        ),
                    ], style={'marginBottom': '20px'}),
                    
                    # Advanced visualization options
                    html.Div([
                        html.Label("Additional Visualizations:"),
                        dcc.Checklist(
                            id='additional-visualizations',
                            options=[
                                {'label': 'Show All Metrics', 'value': 'all_metrics'},
                                {'label': 'Show Correlations', 'value': 'correlations'},
                                {'label': 'Show Statistics', 'value': 'statistics'}
                            ],
                            value=[],
                        ),
                    ]),
                    
                    # Refresh data button
                    html.Div([
                        html.Button('Refresh Data', id='refresh-data', n_clicks=0),
                        html.Div(id='refresh-status')
                    ], style={'marginTop': '30px'}),
                    
                ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
                
                # Right Side: Graphs
                html.Div([
                    # Main time series graph
                    html.Div([
                        dcc.Loading(
                            id="loading-main-graph",
                            type="circle",
                            children=[dcc.Graph(id='time-series-graph')]
                        )
                    ], style={'marginBottom': '20px'}),
                    
                    # Additional visualizations (hidden by default)
                    html.Div(id='additional-graphs', children=[
                        # Will be populated by callback
                    ]),
                    
                    # Statistics panel
                    html.Div(id='statistics-panel', style={'display': 'none'})
                    
                ], style={'width': '75%', 'display': 'inline-block', 'padding': '10px'}),
            ], style={'display': 'flex', 'flexWrap': 'wrap'}),
        ]),
        
        # Cloud Functions Statistics Tab
        dcc.Tab(label="Cloud Function Statistics", children=[
            html.Div([
                html.H2("Statistics from Firebase Cloud Functions", style={'textAlign': 'center'}),
                
                # Refresh stats button
                html.Div([
                    html.Button('Refresh Statistics', id='refresh-stats', n_clicks=0),
                    html.Div(id='stats-status')
                ], style={'margin': '20px auto', 'textAlign': 'center'}),
                
                # Stats display
                html.Div(id='cloud-function-stats', children=[
                    # Will be populated by callback
                ], style={'margin': '20px auto', 'maxWidth': '800px'})
            ])
        ]),
        
        # Firebase Authentication Tab
        dcc.Tab(label="Firebase Authentication", children=[
            html.Div([
                html.H2("Firebase Authentication", style={'textAlign': 'center'}),
                
                # Add Firebase SDK scripts directly in the HTML
                html.Div([
                    # These are needed because external_scripts don't always load properly in the deployed app
                    html.Script(src="https://www.gstatic.com/firebasejs/9.22.0/firebase-app-compat.js"),
                    html.Script(src="https://www.gstatic.com/firebasejs/9.22.0/firebase-auth-compat.js"),
                ], id='firebase-scripts'),
                
                # Inline Firebase config script
                html.Script('''
                    // Your web app's Firebase configuration
                    const firebaseConfig = {
                      apiKey: "AIzaSyAiXABLyYhUCRUygQ7y5xYMIL7JTbhByco",
                      authDomain: "dashweb-9ec83.firebaseapp.com",
                      projectId: "dashweb-9ec83",
                      storageBucket: "dashweb-9ec83.appspot.com",
                      messagingSenderId: "714939783002",
                      appId: "1:714939783002:web:e2f3068851379be6394563",
                      measurementId: "G-HZKF4XTQ0L"
                    };
                
                    // Initialize Firebase
                    firebase.initializeApp(firebaseConfig);
                    
                    // Set up authentication after document is loaded
                    document.addEventListener('DOMContentLoaded', function() {
                        // Set up auth elements after a short delay to ensure they're in the DOM
                        setTimeout(function() {
                            const signinButton = document.getElementById('signin-button');
                            const signupButton = document.getElementById('signup-button');
                            const signoutButton = document.getElementById('signout-button');
                            const emailInput = document.getElementById('email-input');
                            const passwordInput = document.getElementById('password-input');
                            const authStatus = document.getElementById('auth-status');
                            
                            if (!signinButton || !signupButton || !signoutButton) {
                                console.log("Firebase Auth elements not found");
                                return;
                            }
                            
                            console.log("Firebase Auth elements found, setting up event listeners");
                            
                            // Set up authentication state listener
                            firebase.auth().onAuthStateChanged(function(user) {
                                if (user) {
                                    // User is signed in
                                    authStatus.innerHTML = `
                                        <p style="text-align: center; color: green;">
                                            Signed in as ${user.email}
                                        </p>
                                    `;
                                } else {
                                    // User is signed out
                                    authStatus.innerHTML = `
                                        <p style="text-align: center; color: #666;">
                                            Not signed in
                                        </p>
                                    `;
                                }
                            });
                            
                            // Sign In
                            signinButton.addEventListener('click', function() {
                                const email = emailInput.value;
                                const password = passwordInput.value;
                                
                                firebase.auth().signInWithEmailAndPassword(email, password)
                                    .then((userCredential) => {
                                        // Signed in
                                        const user = userCredential.user;
                                        console.log("User signed in:", user.email);
                                    })
                                    .catch((error) => {
                                        console.error("Error signing in:", error);
                                        authStatus.innerHTML = `
                                            <p style="text-align: center; color: red;">
                                                Error: ${error.message}
                                            </p>
                                        `;
                                    });
                            });
                            
                            // Sign Up
                            signupButton.addEventListener('click', function() {
                                const email = emailInput.value;
                                const password = passwordInput.value;
                                
                                firebase.auth().createUserWithEmailAndPassword(email, password)
                                    .then((userCredential) => {
                                        // Signed up
                                        const user = userCredential.user;
                                        console.log("User signed up:", user.email);
                                    })
                                    .catch((error) => {
                                        console.error("Error signing up:", error);
                                        authStatus.innerHTML = `
                                            <p style="text-align: center; color: red;">
                                                Error: ${error.message}
                                            </p>
                                        `;
                                    });
                            });
                            
                            // Sign Out
                            signoutButton.addEventListener('click', function() {
                                firebase.auth().signOut()
                                    .then(() => {
                                        console.log("User signed out");
                                    })
                                    .catch((error) => {
                                        console.error("Error signing out:", error);
                                    });
                            });
                        }, 1000);
                    });
                '''),
                
                # Authentication form
                html.Div([
                    html.Div([
                        html.Label("Email:"),
                        dcc.Input(id="email-input", type="email", placeholder="Enter your email", style={'width': '100%'})
                    ], style={'marginBottom': '15px'}),
                    
                    html.Div([
                        html.Label("Password:"),
                        dcc.Input(id="password-input", type="password", placeholder="Enter your password", style={'width': '100%'})
                    ], style={'marginBottom': '15px'}),
                    
                    html.Div([
                        html.Button("Sign In", id="signin-button", style={'marginRight': '10px'}),
                        html.Button("Sign Up", id="signup-button"),
                        html.Button("Sign Out", id="signout-button", style={'marginLeft': '10px'}),
                    ], style={'marginTop': '20px'}),
                    
                    # Auth status display
                    html.Div(id="auth-status", children=[
                        html.P("Not signed in", style={'textAlign': 'center', 'color': '#666'})
                    ], style={'marginTop': '20px', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'})
                ], style={'maxWidth': '400px', 'margin': '30px auto', 'padding': '20px', 'boxShadow': '0 0 10px rgba(0,0,0,0.1)', 'backgroundColor': 'white', 'borderRadius': '5px'}),
                
                # Custom div for Firebase Javascript interaction
                html.Div(id='firebase-auth-container')
            ])
        ])
    ]),
    
    # Footer
    html.Footer([
        html.P("Interactive Dashboard with Sensor Data, Firebase, and AI Predictions", 
               style={'textAlign': 'center', 'color': '#666'})
    ], style={'padding': '1rem', 'marginTop': '2rem', 'borderTop': '1px solid #eee'})
], style={'fontFamily': 'Arial, sans-serif', 'margin': '0 auto', 'maxWidth': '1600px'})

# Callback to refresh data
@callback(
    [Output('refresh-status', 'children'),
     Output('date-range', 'max_date_allowed'),
     Output('date-range', 'end_date')],
    Input('refresh-data', 'n_clicks'),
    Input('data-source-selector', 'value')
)
def refresh_data(n_clicks, data_source):
    global df, prediction_df, sensor_manager
    
    # Update data source if changed
    if sensor_manager.data_source != data_source:
        sensor_manager = SensorDataManager(data_source=data_source)
    
    # Get fresh data
    df = sensor_manager.get_sensor_data(days=100)
    
    # Retrain models with new data
    prediction_model.train_models(df)
    
    # Make new predictions
    prediction_df = prediction_model.predict_next_values(df, days_ahead=7)
    
    # Try to save to Firebase
    if firebase_db:
        save_data_to_firebase(firebase_db, "sensor_data", df)
        save_data_to_firebase(firebase_db, "predictions", prediction_df)
    
    # Return update status and new date range info
    max_date = df['date'].max()
    return f"Data refreshed at {datetime.now().strftime('%H:%M:%S')}", max_date, max_date

# Define callback to update the graph based on dropdown selection
@callback(
    Output('time-series-graph', 'figure'),
    [Input('metric-selector', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('show-predictions', 'value')]
)
def update_graph(selected_metric, start_date, end_date, show_predictions):
    # Filter data by date range
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    # Create figure
    fig = go.Figure()
    
    # Add actual data
    fig.add_trace(go.Scatter(
        x=filtered_df['date'],
        y=filtered_df[selected_metric],
        mode='lines+markers',
        name=METRICS[selected_metric]['label'],
        line=dict(color=METRICS[selected_metric]['color']),
        marker=dict(size=6)
    ))
    
    # Add predictions if enabled
    if show_predictions == 'yes' and prediction_df is not None:
        fig.add_trace(go.Scatter(
            x=prediction_df['date'],
            y=prediction_df[selected_metric],
            mode='lines+markers',
            name=f"Predicted {METRICS[selected_metric]['label']}",
            line=dict(color=METRICS[selected_metric]['color'], dash='dash'),
            marker=dict(symbol='circle-open', size=8)
        ))
    
    # Update layout
    fig.update_layout(
        title=f"{METRICS[selected_metric]['label']} Over Time",
        xaxis_title="Date",
        yaxis_title=METRICS[selected_metric]['label'],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40),
        hovermode="x unified"
    )
    
    return fig

# Callback to update additional visualizations
@callback(
    Output('additional-graphs', 'children'),
    [Input('additional-visualizations', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('metric-selector', 'value')]
)
def update_additional_graphs(selected_visualizations, start_date, end_date, primary_metric):
    # Filter data by date range
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    graphs = []
    
    # Show all metrics on one graph
    if 'all_metrics' in selected_visualizations:
        # Create a figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add all metrics
        for i, metric in enumerate(METRICS.keys()):
            # Use secondary y-axis for pressure (different scale)
            use_secondary = metric == 'pressure'
            
            fig.add_trace(
                go.Scatter(
                    x=filtered_df['date'],
                    y=filtered_df[metric],
                    mode='lines',
                    name=METRICS[metric]['label'],
                    line=dict(color=METRICS[metric]['color'])
                ),
                secondary_y=use_secondary
            )
        
        # Add titles
        fig.update_layout(
            title_text="All Metrics Over Time",
            template="plotly_white",
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=50, b=40),
            hovermode="x unified"
        )
        
        # Set y-axes titles
        fig.update_yaxes(title_text="Temperature (°C) / Humidity (%)", secondary_y=False)
        fig.update_yaxes(title_text="Pressure (hPa)", secondary_y=True)
        
        graphs.append(html.Div([
            dcc.Graph(figure=fig)
        ], style={'marginBottom': '20px'}))
    
    # Show correlation heatmap
    if 'correlations' in selected_visualizations:
        # Create correlation matrix
        corr_matrix = filtered_df[['temperature', 'humidity', 'pressure']].corr()
        
        # Create heatmap
        heatmap_fig = px.imshow(
            corr_matrix,
            text_auto=True,
            color_continuous_scale='RdBu_r',
            title="Correlation Between Metrics",
            labels=dict(x="Metric", y="Metric", color="Correlation"),
            zmin=-1, zmax=1
        )
        
        heatmap_fig.update_layout(height=350)
        
        graphs.append(html.Div([
            dcc.Graph(figure=heatmap_fig)
        ], style={'marginBottom': '20px'}))
    
    # Show statistics
    if 'statistics' in selected_visualizations:
        # Create a distribution plot for the primary metric
        hist_fig = px.histogram(
            filtered_df, 
            x=primary_metric, 
            marginal="box",
            title=f"Distribution of {METRICS[primary_metric]['label']}",
            color_discrete_sequence=[METRICS[primary_metric]['color']]
        )
        
        hist_fig.update_layout(height=350)
        
        graphs.append(html.Div([
            dcc.Graph(figure=hist_fig)
        ]))
        
        # Add basic statistics table
        stats_df = filtered_df[['temperature', 'humidity', 'pressure']].describe().round(2)
        
        stats_fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Statistic'] + [METRICS[m]['label'] for m in METRICS],
                fill_color='paleturquoise',
                align='left',
                font=dict(size=12)
            ),
            cells=dict(
                values=[stats_df.index] + [stats_df[m] for m in METRICS],
                fill_color='lavender',
                align='left',
                font=dict(size=11)
            )
        )])
        
        stats_fig.update_layout(
            title="Statistical Summary",
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
        )
        
        graphs.append(html.Div([
            dcc.Graph(figure=stats_fig)
        ]))
    
    return graphs

# New callback for cloud function statistics
@callback(
    [Output('cloud-function-stats', 'children'),
     Output('stats-status', 'children')],
    Input('refresh-stats', 'n_clicks')
)
def update_cloud_function_stats(n_clicks):
    """Update statistics from Firebase Cloud Functions"""
    if n_clicks == 0:
        # Initial load - try to get stats
        stats = firebase_functions.get_stats()
        if stats:
            return create_stats_display(stats), "Statistics loaded successfully"
        else:
            return [html.Div([
                html.P("Cloud Functions not yet set up or unavailable.", style={'textAlign': 'center'}),
                html.P([
                    "Follow the instructions to set up Firebase Cloud Functions: ",
                    html.A("Firebase Setup Instructions", 
                           href="https://firebase.google.com/docs/functions/get-started",
                           target="_blank")
                ], style={'textAlign': 'center'})
            ])], "Cloud Functions not available"
    
    # Refresh button clicked
    stats = firebase_functions.get_stats()
    
    if stats:
        return create_stats_display(stats), f"Statistics refreshed at {datetime.now().strftime('%H:%M:%S')}"
    else:
        return [html.Div([
            html.P("Unable to retrieve statistics from Cloud Functions.", style={'textAlign': 'center'}),
            html.P("Make sure you have deployed the Cloud Functions and your app has internet access.", 
                  style={'textAlign': 'center'})
        ])], f"Failed to refresh at {datetime.now().strftime('%H:%M:%S')}"

def create_stats_display(stats_data):
    """Create a display for the statistics data"""
    if not stats_data or 'stats' not in stats_data or not stats_data['stats']:
        return [html.P("No statistics available yet.", style={'textAlign': 'center'})]
    
    stats_list = stats_data['stats']
    
    # Create cards for each statistic
    cards = []
    for stat in stats_list:
        stat_type = stat.get('type', 'unknown')
        value = stat.get('value', 'N/A')
        timestamp = stat.get('timestamp', None)
        
        # Format timestamp if it exists
        timestamp_str = "N/A"
        if timestamp:
            if isinstance(timestamp, dict) and '_seconds' in timestamp:
                # Handle Firestore timestamp format
                timestamp_str = datetime.fromtimestamp(timestamp['_seconds']).strftime('%Y-%m-%d %H:%M:%S')
            else:
                # Try to parse as string
                try:
                    timestamp_str = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    timestamp_str = str(timestamp)
        
        # Create a card
        card = html.Div([
            html.H4(stat_type.replace('_', ' ').title(), style={'margin': '0'}),
            html.H3(f"{value:.2f}" if isinstance(value, (int, float)) else value, 
                   style={'color': '#0074D9', 'margin': '10px 0'}),
            html.P(f"Samples: {stat.get('samples', 'N/A')}"),
            html.P(f"Timestamp: {timestamp_str}", style={'color': '#666', 'fontSize': '0.8rem'})
        ], style={
            'padding': '20px',
            'margin': '10px',
            'borderRadius': '5px',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.1)',
            'backgroundColor': 'white',
            'display': 'inline-block',
            'width': 'calc(50% - 40px)',
            'verticalAlign': 'top'
        })
        
        cards.append(card)
    
    # If no cards were created
    if not cards:
        return [html.P("No statistics available yet.", style={'textAlign': 'center'})]
    
    return cards

# Make app object itself WSGI compatible
if __name__ != "__main__":
    # When imported by Gunicorn, make the app object itself callable
    # by using a trick to reassign the app variable to the underlying server
    callable_app = app.server
    app = callable_app

# Run the app if this file is executed directly
if __name__ == "__main__":
    app.run_server(debug=True) 