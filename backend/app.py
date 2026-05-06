import os
import re
import json
import requests
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Assuming your db.py is set up correctly in the same directory
from db import shipments_collection

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Rate Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def fetch_serper_data(query):
    try:
        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        for attempt in range(3):
            try:
                response = requests.post(url, headers=headers, json={"q": query}, timeout=10)
                response.raise_for_status()
                return response.json()
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as ce:
                print(f"[SERPER WARNING] Attempt {attempt + 1} failed: {ce}")
                time.sleep(1)
                if attempt == 2: raise ce
    except Exception as e:
        print(f"[SERPER ERROR] Failed to fetch data: {e}")
        return None

def extract_json_from_text(text):
    text = text.replace("```json", "").replace("```", "").strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as e:
            print(f"[JSON PARSE ERROR]: {e}")
            return None
    return None

def analyze_route_with_gemma(route_list, serper_context):
    try:
        today_date = datetime.now().strftime("%A, %B %d, %Y")
        prompt = f"""
        You are an AI logistics expert. Today's date is {today_date}.
        Analyze this route: {', '.join(route_list)}.
        Context from web search: {serper_context}
        
        Return a JSON object with:
        - risk_score (0-100)
        - affected_location (string, or "None")
        - suggested_route (ARRAY of strings)
        - situation_analysis (string, 2-3 sentences)
        
        Return ONLY valid JSON.
        """
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "google/gemini-2.0-flash", # Updated to stable Flash identifier
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
        
        for attempt in range(3):
            try:
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=15)
                
                # --- NEW: CRITICAL LOGGING ---
                if response.status_code != 200:
                    print(f"[OPENROUTER FULL ERROR]: {response.status_code} - {response.text}")
                
                response.raise_for_status()
                break
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 429:
                    print(f"[AI WARNING] Rate limit (429). Retrying... {attempt + 1}/3")
                    time.sleep(5)
                    continue
                raise e
        
        result_text = response.json()["choices"][0]["message"]["content"]
        parsed_json = extract_json_from_text(result_text)
        return parsed_json if parsed_json else None
            
    except Exception as e:
        print(f"[AI ERROR] Analysis failed: {e}")
        return None

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "Smartpath API is running", "version": "1.1"}), 200

@app.route('/api/shipments', methods=['GET'])
def get_shipments():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
        
    shipments = list(shipments_collection.find({"user_id": user_id}, {'_id': 0}))
    
    # Anti-Browser Caching
    response = make_response(jsonify(shipments))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response, 200

@app.route('/api/shipments', methods=['POST'])
@limiter.limit("1 per 3 seconds")
def create_shipment():
    data = request.json
    user_id = data.get('user_id')
    route_string = data.get('route')
    
    if not user_id or not route_string:
        return jsonify({"error": "Missing data"}), 400
        
    route_list = [city.strip() for city in route_string.split(',')]
    
    # 1. Cache Check (10-minute window)
    ten_minutes_ago = (datetime.now() - timedelta(minutes=10)).isoformat()
    existing = shipments_collection.find_one({
        "user_id": user_id,
        "original_route": route_list,
        "timestamp": {"$gte": ten_minutes_ago}
    })

    if existing:
        if '_id' in existing: del existing['_id']
        return jsonify(existing), 201
    
    # 2. Traffic Context
    search_query = f"live road traffic accidents closures weather {' to '.join(route_list)}"
    serper_data = fetch_serper_data(search_query)
    serper_context = ""
    if serper_data and 'organic' in serper_data:
        serper_context = " ".join([item.get('snippet', '') for item in serper_data['organic'][:3]])
    
    # 3. AI Prediction
    ai_result = analyze_route_with_gemma(route_list, serper_context)
    
    # Normalizer Fallback
    if not ai_result:
        ai_result = {
            "risk_score": 15,
            "affected_location": "None",
            "suggested_route": route_list,
            "situation_analysis": "No detailed situation analysis available."
        }

    final_ai_result = {
        "risk_score": int(ai_result.get("risk_score", 15)),
        "affected_location": ai_result.get("affected_location", "None"),
        "suggested_route": ai_result.get("suggested_route", route_list),
        "situation_analysis": ai_result.get("situation_analysis", "No detailed analysis available."),
        "state": "Monitoring" if int(ai_result.get("risk_score", 0)) < 50 else "Action Required"
    }
    
    shipment_doc = {
        "user_id": user_id,
        "original_route": route_list,
        "ai_result": final_ai_result, 
        "timestamp": datetime.now().isoformat()
    }
    
    shipments_collection.insert_one(shipment_doc)
    if '_id' in shipment_doc: del shipment_doc['_id']
    return jsonify(shipment_doc), 201

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)