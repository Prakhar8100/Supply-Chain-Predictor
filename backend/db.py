import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/smartpath")

def setup_db():
    client = MongoClient(MONGO_URI)
    db = client.get_database()
    shipments = db["shipments"]
    
    # Create index on user_id for fast filtering
    shipments.create_index("user_id")
    return shipments

shipments_collection = setup_db()
