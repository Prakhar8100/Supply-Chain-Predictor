import os
from pymongo import MongoClient
from dotenv import load_dotenv

# 1. Force reload of the .env file
load_dotenv()

# 2. Get URI (Ensure your .env file has MONGO_URI=...)
MONGO_URI = os.getenv("MONGO_URI")

def setup_db():
    if not MONGO_URI:
        print("⚠️ WARNING: MONGO_URI not found in .env. Falling back to localhost.")
        client = MongoClient("mongodb://localhost:27017")
    else:
        print(f"✅ Connecting to MongoDB using URI: {MONGO_URI}")
        client = MongoClient(MONGO_URI)
    
    # 3. EXPLICITLY name your database here 
    # (Replace 'smartpath_db' with your actual Atlas database name)
    db = client["smartpath_db"] 
    
    shipments = db["shipments"]
    
    # Create index on user_id for fast filtering
    shipments.create_index("user_id")
    return shipments

shipments_collection = setup_db()