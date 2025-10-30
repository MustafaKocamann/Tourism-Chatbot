import sqlite3
import json
from datetime import datetime
from pathlib import Path
from config.settings import DATABASE_PATH

class UserDatabase:
    """Kullanıcı oturumları ve geçmişi için SQLite veritabanı"""
    
    def __init__(self):
        Path("data").mkdir(exist_ok=True)
        self.conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """Tabloları oluştur"""
        # Kullanıcı tablosu
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                created_at TEXT,
                last_active TEXT,
                preferences TEXT
            )
        """)
        
        # Sohbet geçmişi tablosu
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                timestamp TEXT,
                user_message TEXT,
                bot_message TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Seyahat planları tablosu
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS travel_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                created_at TEXT,
                title TEXT,
                city TEXT,
                date_range TEXT,
                plan_data TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Favori yerler tablosu
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                city TEXT,
                category TEXT,
                notes TEXT,
                added_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        self.conn.commit()
    
    def create_user(self, user_id: str, preferences: dict = None):
        """Yeni kullanıcı oluştur"""
        try:
            now = datetime.now().isoformat()
            prefs = json.dumps(preferences or {})
            
            self.cursor.execute("""
                INSERT OR IGNORE INTO users (user_id, created_at, last_active, preferences)
                VALUES (?, ?, ?, ?)
            """, (user_id, now, now, prefs))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"DB Error: {e}")
            return False
    
    def update_last_active(self, user_id: str):
        """Son aktivite zamanını güncelle"""
        now = datetime.now().isoformat()
        self.cursor.execute("""
            UPDATE users SET last_active = ? WHERE user_id = ?
        """, (now, user_id))
        self.conn.commit()
    
    def save_chat(self, user_id: str, user_message: str, bot_message: str):
        """Sohbet kaydı kaydet"""
        try:
            timestamp = datetime.now().isoformat()
            
            self.cursor.execute("""
                INSERT INTO chat_history (user_id, timestamp, user_message, bot_message)
                VALUES (?, ?, ?, ?)
            """, (user_id, timestamp, user_message, bot_message))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"DB Error: {e}")
            return False
    
    def get_chat_history(self, user_id: str, limit: int = 10):
        """Kullanıcının sohbet geçmişini al"""
        self.cursor.execute("""
            SELECT timestamp, user_message, bot_message 
            FROM chat_history 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (user_id, limit))
        
        results = self.cursor.fetchall()
        return [
            {
                "timestamp": r[0],
                "user_message": r[1],
                "bot_message": r[2]
            }
            for r in reversed(results)
        ]
    
    def save_travel_plan(self, user_id: str, title: str, city: str, 
                         date_range: str, plan_data: dict):
        """Seyahat planı kaydet"""
        try:
            timestamp = datetime.now().isoformat()
            plan_json = json.dumps(plan_data)
            
            self.cursor.execute("""
                INSERT INTO travel_plans (user_id, created_at, title, city, date_range, plan_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, timestamp, title, city, date_range, plan_json))
            
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"DB Error: {e}")
            return None
    
    def get_travel_plans(self, user_id: str):
        """Kullanıcının tüm planlarını al"""
        self.cursor.execute("""
            SELECT id, created_at, title, city, date_range, plan_data
            FROM travel_plans
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        
        results = self.cursor.fetchall()
        return [
            {
                "id": r[0],
                "created_at": r[1],
                "title": r[2],
                "city": r[3],
                "date_range": r[4],
                "plan_data": json.loads(r[5])
            }
            for r in results
        ]
    
    def add_favorite(self, user_id: str, city: str, category: str, notes: str = ""):
        """Favori şehir/yer ekle"""
        try:
            timestamp = datetime.now().isoformat()
            
            self.cursor.execute("""
                INSERT INTO favorites (user_id, city, category, notes, added_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, city, category, notes, timestamp))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"DB Error: {e}")
            return False
    
    def get_favorites(self, user_id: str):
        """Kullanıcının favorilerini al"""
        self.cursor.execute("""
            SELECT city, category, notes, added_at
            FROM favorites
            WHERE user_id = ?
            ORDER BY added_at DESC
        """, (user_id,))
        
        results = self.cursor.fetchall()
        return [
            {
                "city": r[0],
                "category": r[1],
                "notes": r[2],
                "added_at": r[3]
            }
            for r in results
        ]
    
    def close(self):
        """Bağlantıyı kapat"""
        self.conn.close()