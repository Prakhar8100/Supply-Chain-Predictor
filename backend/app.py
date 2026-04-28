import os
import re
import json
import requests
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from db import shipments_collection

load_dotenv()

app = Flask(__name__)
CORS(app)

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
                if attempt == 2:
                    raise ce
    except Exception as e:
        print(f"[SERPER ERROR] Failed to fetch data for query '{query}': {e}")
        return None

def extract_json_from_text(text):
    # Strip out markdown that crashes standard JSON parsers
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
        # Grab today's real date to ground the AI in the present timeline
        today_date = datetime.now().strftime("%A, %B %d, %Y")

        prompt = f"""
        You are an AI logistics expert. Today's date is {today_date}.
        Analyze this route: {', '.join(route_list)}.
        Context from web search: {serper_context}
        
        If there are any risks, identify the specific 'affected_location' city.
        Return a JSON object with:
        - risk_score (0-100)
        - affected_location (string, or "None" if safe)
        - suggested_route (ARRAY of strings, removing the blocked city if risk_score > 50)
        - situation_analysis (string, a 2-3 sentence summary explaining the current weather/traffic situation and if any alternative routes are better)
        
        Return ONLY valid JSON. Do not use markdown blocks.
        """
        
        keywords = ["closed", "landslide", "blocked", "heavy traffic", "ice to snow", "accident", "crash", "jam", "severe traffic"]
        if any(kw in serper_context.lower() for kw in keywords):
            prompt = "PRIORITY WARNING: Severe disruption detected in search results! Adjust risk score heavily.\n" + prompt

        print(f"[AI REQUEST] Sending prompt to Google Gemma 3 via OpenRouter...")
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "google/gemma-3-12b-it:free",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
        
        for attempt in range(3):
            try:
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=15)
                response.raise_for_status()
                break
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    print(f"[AI WARNING] Rate limit hit (429). Retrying in 5 seconds... (Attempt {attempt + 1}/3)")
                    time.sleep(5)
                    if attempt == 2:
                        raise e
                else:
                    raise e
        
        result_text = response.json()["choices"][0]["message"]["content"]
        print(f"[AI RESPONSE] {result_text}")
        
        parsed_json = extract_json_from_text(result_text)
        if parsed_json:
            return parsed_json
        else:
            raise ValueError("Could not extract JSON from response")
            
    except Exception as e:
        print(f"[AI ERROR] Analysis failed: {e}")
        return None

# --- NEW: Health Check Route to fix Render 404 Errors ---
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "Smartpath API is running natively", "version": "1.0"}), 200

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/shipments', methods=['GET'])
def get_shipments():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
        
    shipments = list(shipments_collection.find({"user_id": user_id}, {'_id': 0}))
    return jsonify(shipments), 200

@app.route('/api/shipments', methods=['POST'])
def create_shipment():
    data = request.json
    user_id = data.get('user_id')
    route_string = data.get('route')
    
    if not user_id or not route_string:
        return jsonify({"error": "user_id and route are required"}), 400
        
    route_list = [city.strip() for city in route_string.split(',')]
    
    print(f"[INFO] Processing shipment for {user_id} with route {route_list}")
    
    # Check traffic for the route
    search_query = f"live road traffic accidents road closures weather {' to '.join(route_list)}"
    serper_data = fetch_serper_data(search_query)
    
    serper_context = ""
    if serper_data and 'organic' in serper_data:
        snippets = [item.get('snippet', '') for item in serper_data['organic'][:3]]
        serper_context = " ".join(snippets)
    
    print(f"[INFO] Serper Context: {serper_context}")
    
    ai_result = analyze_route_with_gemma(route_list, serper_context)
    
    # --- THE BULLETPROOF DATA NORMALIZER ---
    if not ai_result:
        ai_result = {}

    risk_score = int(ai_result.get("risk_score", 15))
    affected_location = ai_result.get("affected_location", "")

    # 1. Guarantee suggested_route is an array (Prevents React from crashing)
    suggested_route = ai_result.get("suggested_route", route_list)
    if isinstance(suggested_route, str):
        suggested_route = [c.strip() for c in suggested_route.split(",")]
    if not isinstance(suggested_route, list):
        suggested_route = route_list

    # 2. THE BETTER ROUTE FEATURE (Hackathon Override)
    # If AI detects risk but forgets to reroute, the backend forces it here
    if risk_score > 50 and affected_location and affected_location.lower() != "none":
        recalculated_route = [city for city in route_list if city.strip().lower() != affected_location.strip().lower()]
        # Ensure we don't accidentally delete the whole route
        if len(recalculated_route) > 1:
            suggested_route = recalculated_route

    final_ai_result = {
        "risk_score": risk_score,
        "affected_location": affected_location if affected_location else "None",
        "suggested_route": suggested_route,
        "situation_analysis": ai_result.get("situation_analysis", "No detailed situation analysis available."),
        "state": "Monitoring" if risk_score < 50 else "Action Required"
    }
    
    shipment_doc = {
        "user_id": user_id,
        "original_route": route_list,
        "ai_result": final_ai_result, 
        "timestamp": data.get('timestamp', '')
    }
    
    shipments_collection.insert_one(shipment_doc)
    
    # Remove _id for JSON serialization
    if '_id' in shipment_doc:
        del shipment_doc['_id']
        
    return jsonify(shipment_doc), 201

if __name__ == '__main__':
    # --- FIXED: Render requires binding to 0.0.0.0 and a dynamic port ---
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)