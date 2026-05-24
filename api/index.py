"""Vercel serverless function entry point for Flask app."""
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app

# Vercel serverless handler
def handler(event, context):
    """Vercel serverless handler."""
    return app(event, context)

# For local testing
if __name__ == "__main__":
    app.run(debug=True)
