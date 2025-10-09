from pymongo import MongoClient
from pymongo.database import Database
from app.core.config import settings

class MongoDB:
    client: MongoClient 
    db: Database 

mongodb = MongoDB()

def connect_mongodb():
    """Connect to MongoDB"""
    mongodb.client = MongoClient(settings.mongodb_url)
    mongodb.db = mongodb.client[settings.mongodb_db_name]
    
    # Create indexes for better performance
    mongodb.db.namaste_codes.create_index([("code", 1)])
    mongodb.db.namaste_codes.create_index([("display", "text")])
    mongodb.db.icd11_codes.create_index([("code", 1)])
    mongodb.db.icd11_codes.create_index([("display", "text")])
    
    print("✅ Connected to MongoDB")

def close_mongodb():
    """Close MongoDB connection"""
    if mongodb.client:
        mongodb.client.close()
        print("✅ Closed MongoDB connection")

def get_mongodb() -> Database:
    """Get MongoDB database instance"""
    return mongodb.db