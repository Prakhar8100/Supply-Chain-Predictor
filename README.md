# 🚚 Supply Chain Predictor (SmartPath)

> **AI-Powered Logistics Rerouter & Supply Chain Risk Predictor**

SmartPath is an intelligent logistics platform that analyzes shipment routes in real-time using live web data and AI-driven insights. It fetches real-time traffic, accidents, and weather data via Serper API, then uses Google Gemma 3 to assess risks and automatically generate optimized alternative routes when disruptions are detected.

## 🎯 Key Features

- **🔍 Live Disruption Detection**: Real-time web scraping for traffic accidents, road closures, and severe weather conditions
- **🤖 AI-Powered Route Optimization**: Google Gemma 3 12B analyzes risks and dynamically suggests alternative routes
- **⚡ Smart Rate-Limit Handling**: Automatic 429 error recovery with graceful backoff mechanism for reliable API operations
- **🏢 Zero-Login Multi-Tenancy**: Fleet-based data isolation with no authentication required
- **📊 Real-Time Dashboard**: Glassmorphism UI with color-coded risk indicators (Monitoring vs. Action Required)
- **🗺️ Route Intelligence**: Automatic removal of blocked cities from suggested routes when risk is detected

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 19.2.5
- **Build Tool**: Vite 8.0
- **UI Components**: Lucide React (Icons)
- **HTTP Client**: Axios 1.15.2
- **Styling**: CSS3 (Glassmorphism, Custom Theme)

### Backend
- **Framework**: Flask 3.0.3
- **Database**: MongoDB 4.7+
- **CORS**: Flask-CORS 4.0.1
- **Environment**: Python-dotenv 1.0.1
- **HTTP**: Requests 2.31.0

### External APIs
- **Search Data**: [Serper.dev](https://serper.dev) (Google Search API)
- **AI Model**: [OpenRouter](https://openrouter.ai) - Google Gemma 3 12B (Free Tier)

---

## 📋 Prerequisites

Before you begin, ensure you have:
- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (3.9+)
- [MongoDB](https://www.mongodb.com/try/download/community) (Local or Atlas)
- API Keys:
  - Serper API Key (free tier available at [serper.dev](https://serper.dev))
  - OpenRouter API Key (free tier available at [openrouter.ai](https://openrouter.ai))

---

## ⚙️ Setup & Installation

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the `backend/` directory:
   ```env
   MONGO_URI=Your_MongoDB_URL
   SERPER_API_KEY=your_serper_api_key_here
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   FLASK_ENV=development
   ```

5. **Run the backend server**:
   ```bash
   python app.py
   ```
   Server will start at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```
   Application will open at `http://localhost:5173`

4. **Build for production**:
   ```bash
   npm run build
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

## ☁️ Render Deployment (Backend)

To deploy the Flask backend on [Render](https://render.com/), follow these steps:

1. Create a new **Web Service** on Render and connect your repository.
2. Use the following configuration:
   - **Root Directory**: `backend` (or leave blank if using the root `requirements.txt`)
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py` (if Root Directory is `backend`) OR `cd backend && python app.py` (if no Root Directory is set)
3. Add your Environment Variables under the **Environment** tab:
   - `MONGO_URI`
   - `SERPER_API_KEY`
   - `OPENROUTER_API_KEY`

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
