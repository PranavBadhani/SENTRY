from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

from agent import generate_swarm_payload
import torch
from model import TimeSeriesAnomalyTransformer, calculate_time_deltas
import os

app = Flask(__name__)
CORS(app) 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - SENTRY-SERVER - %(message)s')

# --- TRANSFORMER MODEL LOADING ---
device = torch.device("cpu")
model = TimeSeriesAnomalyTransformer()
model_path = os.path.join(os.path.dirname(__file__), "model.pth")

if os.path.exists(model_path):
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    logging.info("Neural Engine Online: Primary Transformer Model loaded successfully.")
else:
    logging.warning("CRITICAL: model.pth not found. The model must be trained before the analysis pipeline becomes fully operational.")



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

@app.route('/analyze', methods=['POST'])
def analyze_corpus():
    try:
        data = request.get_json()
        corpus = data.get('corpus', [])
        
        if not corpus:
            return jsonify([]), 200
            
        logging.info(f"Analysis Request Received: {len(corpus)} nodes passing through Time-Series Transformer...")
        
        # We must process the corpus chronologically to check the time gaps
        # But we must preserve the original UI shuffled order!
        indexed_corpus = [(i, node) for i, node in enumerate(corpus)]
        sorted_corpus = sorted(indexed_corpus, key=lambda x: x[1].get('timestamp', 0))
        
        timestamps_ms = [x[1].get('timestamp', 0) for x in sorted_corpus]
        deltas = calculate_time_deltas(timestamps_ms)
        
        results = [None] * len(corpus)
        
        with torch.no_grad():
            tensor_input = torch.tensor(deltas, dtype=torch.float32).unsqueeze(-1).unsqueeze(0).to(device)
            preds = model(tensor_input).squeeze(0) # shape: (seq_len)
            
            for ptr, (original_index, node) in enumerate(sorted_corpus):
                prob = preds[ptr].item()
                is_swarm = prob > 0.5
                
                node['flagged'] = is_swarm
                node['threat_probability'] = prob
                
                results[original_index] = node
                
        logging.info("Analysis Complete. Dispatching results perfectly mapped to original shuffled order.")
        return jsonify(results), 200

    except Exception as e:
        logging.error(f"Transformer Failure: {str(e)}")
        return jsonify({"error": "Neural Backend Error"}), 500


@app.route('/', methods=['GET'])
def health_check():
    return "SENTRY API GATEWAY IS ONLINE. Awaiting frontend POST requests on /generate.", 200

if __name__ == '__main__':
    print("\n" + "="*50)
    print(" /// SENTRY API GATEWAY ONLINE              ///")
    print(" /// AWAITING FRONTEND CONNECTION PORT 5000 ///")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)