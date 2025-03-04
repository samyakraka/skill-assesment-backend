import os
import sys

# Add the current directory to Python path to make the app package visible
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, current_dir)

from app import create_app

app = create_app()

if __name__ == '__main__':
    print(f"Starting Flask server at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)