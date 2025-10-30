from datetime import datetime, timedelta
from langchain_community.chat_message_histories import ChatMessageHistory
from utils.database import UserDatabase
import hashlib

class SessionManager:
    """Kullanıcı oturumlarını yönet"""
    
    def __init__(self):
        self.sessions = {}  # user_id -> ChatMessageHistory
        self.db = UserDatabase()
    
    def generate_user_id(self, ip_address: str) -> str:
        """IP adresinden kullanıcı ID'si oluştur"""
        return hashlib.md5(ip_address.encode()).hexdigest()[:16]
    
    def get_session(self, user_id: str) -> ChatMessageHistory:
        """Kullanıcı oturumunu al veya oluştur"""
        if user_id not in self.sessions:
            self.sessions[user_id] = ChatMessageHistory()
            self.db.create_user(user_id)
            
            # Önceki sohbet geçmişini yükle
            history = self.db.get_chat_history(user_id, limit=5)
            for item in history:
                self.sessions[user_id].add_user_message(item["user_message"])
                self.sessions[user_id].add_ai_message(item["bot_message"])
        
        self.db.update_last_active(user_id)
        return self.sessions[user_id]
    
    def save_message(self, user_id: str, user_message: str, bot_message: str):
        """Mesajı veritabanına kaydet"""
        self.db.save_chat(user_id, user_message, bot_message)
    
    def clear_session(self, user_id: str):
        """Kullanıcı oturumunu temizle"""
        if user_id in self.sessions:
            del self.sessions[user_id]
    
    def get_user_stats(self, user_id: str) -> dict:
        """Kullanıcı istatistiklerini al"""
        history = self.db.get_chat_history(user_id, limit=100)
        plans = self.db.get_travel_plans(user_id)
        favorites = self.db.get_favorites(user_id)
        
        return {
            "total_messages": len(history),
            "total_plans": len(plans),
            "total_favorites": len(favorites),
            "recent_cities": list(set([p["city"] for p in plans[-5:]]))
        }


class CacheManager:
    """API sonuçlarını cache'le"""
    
    def __init__(self, expiry_seconds: int = 1800):
        self.cache = {}
        self.expiry = expiry_seconds
    
    def get(self, key: str):
        """Cache'den veri al"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.expiry):
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value):
        """Cache'e veri kaydet"""
        self.cache[key] = (value, datetime.now())
    
    def clear(self):
        """Tüm cache'i temizle"""
        self.cache.clear()