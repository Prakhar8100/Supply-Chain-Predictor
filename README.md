# Supply Chain Predictor (SmartPath)

SmartPath is an AI-driven logistics rerouter and supply chain risk predictor. It analyzes shipment routes in real-time by aggressively scraping Google Search (via Serper) for live road traffic, accidents, and weather data. It then utilizes Google Gemma 3 (via OpenRouter) to assess risks, generate a situation analysis, and automatically provide optimized alternative routes when severe disruptions are detected.

## 🚀 Features

- **Live Disruption Tracking**: Fetches real-time web data specifically targeted at traffic accidents, road closures, and severe weather.
- **AI Rerouting & Situation Analysis**: Uses Google Gemma 3 12B (via OpenRouter) to evaluate risk factors, summarize the ongoing road situation, and dynamically drop blocked cities from the route.
- **Automatic API Rate-Limit Recovery**: Built-in 429 error handling with a graceful backoff-and-retry mechanism for stable AI queries on the free tier.
- **Zero-Login Multi-Tenancy**: Safely separates shipment history by dynamically scoping database queries based on your chosen Fleet/Company name at launch.
- **Dynamic Glassmorphism Dashboard**: Visualizes shipment states (Monitoring vs. Action Required) with real-time, color-coded risk indicators.

## 🛠️ Tech Stack

- **Frontend**: React 19, Vite, Lucide React, CSS3 (Custom Glassmorphism UI)
- **Backend**: Flask (Python), MongoDB, OpenRouter API (Gemma 3), Serper.dev API

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (3.9+)
- [MongoDB](https://www.mongodb.com/try/download/community) (Local or Atlas)

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   Create a `.env` file inside the `backend/` folder:
   ```env
   MONGO_URI=your_mongo_connection_string_here
   SERPER_API_KEY=your_serper_api_key_here
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```
5. Run the backend server:
   ```bash
   python app.py
   ```
   The backend will start on `http://127.0.0.1:5000`.

### 3. Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser at `http://localhost:5173`.

---

## 📊 Usage
1. Upon loading the app, enter your **Fleet/Company Name** in the prompt. This isolates your data from other users.
2. Enter a planned logistics route (e.g., `Delhi, Meerut, Haridwar`).
3. Click **"Optimize Route"** to trigger the AI risk assessment.
4. The system will aggressively scan the web for accidents along your route, display the risk score, provide a situation summary, and give you an AI-Optimized route if necessary!

## 📄 License

This project, **Supply Chain Predictor (SmartPath)**, is licensed under the MIT License. 

All custom source code, proprietary logic, unique UI/UX designs, and specific application architecture contained within this repository are the intellectual property of the repository owner. 

You are free to use, modify, and distribute the core codebase in accordance with the terms of the MIT license, provided that appropriate credit and attribution are explicitly given back to the original author and this repository.
