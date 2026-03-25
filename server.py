from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Import the logic from your agent.py file
from agent import generate_swarm_payload

# Initialize the SENTRY Backend Interface
app = Flask(__name__)

# Enable CORS
CORS(app) 

# Set up terminal logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - SENTRY-SERVER - %(message)s')

# --- API ENDPOINTS ---

@app.route('/generate', methods=['POST'])
def generate_swarm():
    try:
        data = request.get_json()
        target = data.get('target', '#TARGET')
        count = data.get('count', 10)

        logging.info(f"Received swarm request: {count} nodes targeting {target}")
        
        # Trigger the agent logic
        payload = generate_swarm_payload(target=target, count=count)
        
        logging.info("Payload generated successfully. Dispatching to frontend.")
        return jsonify(payload), 200

    except Exception as e:
        logging.error(f"System Failure: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

# Health check route to prevent 404 errors in the browser
@app.route('/', methods=['GET'])
def health_check():
    return "SENTRY API GATEWAY IS ONLINE. Awaiting frontend POST requests on /generate.", 200

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    print("\n" + "="*50)
    print(" /// SENTRY API GATEWAY ONLINE              ///")
    print(" /// AWAITING FRONTEND CONNECTION PORT 5000 ///")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)