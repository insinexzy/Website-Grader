from flask import Flask, request, jsonify
from flask_cors import CORS
from website_grader_v4 import WebsiteGraderV4
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS with specific settings
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "http://127.0.0.1:8000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin"]
    }
})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    try:
        # Test if we can import and instantiate the grader
        grader = WebsiteGraderV4()
        return jsonify({
            'status': 'ok',
            'message': 'Website Grader API is running'
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_website():
    """Analyze a website using the WebsiteGrader"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        logger.debug(f"Received request: {request.data}")
        data = request.get_json()
        
        if not data:
            logger.error("No JSON data received")
            return jsonify({
                'error': 'No JSON data received',
                'message': 'Please provide a URL to analyze'
            }), 400

        url = data.get('url', '').strip()
        if not url:
            logger.error("No URL provided")
            return jsonify({
                'error': 'No URL provided',
                'message': 'Please provide a valid URL to analyze'
            }), 400
        
        logger.info(f"Analyzing URL: {url}")
        grader = WebsiteGraderV4()
        results = grader.analyze_website(url)
        
        if results is None:
            logger.error(f"Analysis failed for URL: {url}")
            return jsonify({
                'error': 'Analysis failed',
                'message': 'Website blocked automated access or could not be reached'
            }), 403
            
        logger.info(f"Analysis completed for URL: {url}")
        return jsonify({
            'url': url,
            'status': 'completed',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error analyzing website: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'error': 'Analysis failed',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 