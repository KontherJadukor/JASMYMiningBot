import json
import os
from http.server import BaseHTTPRequestHandler
import requests
from pymongo import MongoClient

# Vercel Environment Variables থেকে টোকেন এবং ডাটাবেজ লিংক নেওয়া হবে
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
WEB_APP_URL = "https://KontherJadukor.github.io/JASMYMiningBot/"
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

MONGO_URI = os.environ.get("MONGODB_URI", "")
client = MongoClient(MONGO_URI)
db = client["jasmy_miner_db"]
users_collection = db["users"]

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            update = json.loads(post_data.decode('utf-8'))
            
            if "message" in update:
                message = update["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "")
                user_id = message["from"]["id"]
                first_name = message["from"].get("first_name", "User")
                
                if text.startswith("/start"):
                    args = text.split(" ")
                    referred_by = args[1] if len(args) > 1 else None
                    
                    existing_user = users_collection.find_one({"user_id": user_id})
                    
                    if not existing_user:
                        user_data = {
                            "user_id": user_id,
                            "first_name": first_name,
                            "balance": 0.0,
                            "mining_speed": 0.01,
                            "tasks_completed": [],
                            "referred_by": referred_by,
                            "referrals": []
                        }
                        users_collection.insert_one(user_data)
                        
                        if referred_by:
                            users_collection.update_one(
                                {"user_id": int(referred_by)},
                                {"$push": {"referrals": user_id}}
                            )
                    
                    payload = {
                        "chat_id": chat_id,
                        "text": f"Hello *{first_name}*! 👋\n\nWelcome to *JASMY Miner Pro*. Your account is active. Click below to start mining:",
                        "parse_mode": "Markdown",
                        "reply_markup": {
                            "inline_keyboard": [
                                [{"text": "🚀 Open JASMY Miner", "web_app": {"url": WEB_APP_URL}}]
                            ]
                        }
                    }
                    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)
                    
        except Exception as e:
            print(f"Error: {e}")

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
        return
