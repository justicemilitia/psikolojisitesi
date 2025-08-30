"""
Alternative entry point for running the application without database operations.
Use this if you're experiencing database connection issues.
"""

# Import the patch_app function from config_override and apply it
# before importing the create_app function
import config_override
config_override.patch_app()

# Now import the create_app function
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)