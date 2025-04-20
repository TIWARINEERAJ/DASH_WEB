from app import app

# This is the object that Gunicorn will use
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True) 