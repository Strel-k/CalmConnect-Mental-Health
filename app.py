from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/welcome', methods=['GET'])
def welcome():
    """
    Endpoint that logs request metadata and returns a welcome message
    """
    # Log request metadata
    logger.info(f"Request received: {request.method} {request.path}")

    # Return JSON response
    return jsonify({
        'message': 'Welcome to the Flask API Service!'
    })

if __name__ == '__main__':
    app.run(debug=True)
