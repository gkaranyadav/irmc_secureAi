# src/core/database.py
import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager
from typing import Dict, Any, List, Optional
import pandas as pd

class Database:
    """
    SQLite database manager for SentinelAI
    Free, file-based, perfect for development and small deployments
    """
    
    def __init__(self, db_path: str = "sentinelai.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Transactions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                card_last4 TEXT,
                amount REAL,
                merchant TEXT,
                timestamp TEXT,
                country TEXT,
                device_id TEXT,
                ip_address TEXT,
                risk_score INTEGER,
                is_fraud INTEGER DEFAULT 0,
                processed_at TEXT
            )
            ''')
            
            # Agents table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                agent_name TEXT,
                version TEXT,
                status TEXT,
                last_active TEXT,
                config TEXT,
                created_at TEXT
            )
            ''')
            
            # Agent logs table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT,
                event_type TEXT,
                details TEXT,
                timestamp TEXT,
                FOREIGN KEY (agent_id) REFERENCES agents (agent_id)
            )
            ''')
            
            # Alerts table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                transaction_id TEXT,
                alert_type TEXT,
                risk_score INTEGER,
                action_taken TEXT,
                timestamp TEXT,
                resolved INTEGER DEFAULT 0,
                FOREIGN KEY (transaction_id) REFERENCES transactions (transaction_id)
            )
            ''')
            
            # Models table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS models (
                model_id TEXT PRIMARY KEY,
                model_name TEXT,
                version TEXT,
                accuracy REAL,
                trained_at TEXT,
                file_path TEXT,
                active INTEGER DEFAULT 1
            )
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def insert_transaction(self, transaction: Dict[str, Any]):
        """Insert a transaction record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT OR REPLACE INTO transactions 
            (transaction_id, card_last4, amount, merchant, timestamp, country, 
             device_id, ip_address, risk_score, is_fraud, processed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction.get('transaction_id'),
                transaction.get('card_last4'),
                transaction.get('amount'),
                transaction.get('merchant'),
                transaction.get('timestamp'),
                transaction.get('country'),
                transaction.get('device_id'),
                transaction.get('ip_address'),
                transaction.get('risk_score', 0),
                transaction.get('is_fraud', 0),
                datetime.utcnow().isoformat()
            ))
            conn.commit()
    
    def get_transactions(self, limit: int = 1000, offset: int = 0) -> List[Dict]:
        """Get recent transactions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT * FROM transactions 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def log_agent_event(self, agent_id: str, event_type: str, details: Dict = None):
        """Log agent event"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO agent_logs (agent_id, event_type, details, timestamp)
            VALUES (?, ?, ?, ?)
            ''', (
                agent_id,
                event_type,
                json.dumps(details or {}),
                datetime.utcnow().isoformat()
            ))
            conn.commit()
    
    def create_alert(self, alert_id: str, transaction_id: str, alert_type: str, 
                    risk_score: int, action_taken: str):
        """Create a fraud alert"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO alerts (alert_id, transaction_id, alert_type, risk_score, 
                               action_taken, timestamp, resolved)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert_id,
                transaction_id,
                alert_type,
                risk_score,
                action_taken,
                datetime.utcnow().isoformat(),
                0
            ))
            conn.commit()
    
    def get_alerts(self, resolved: Optional[bool] = None) -> List[Dict]:
        """Get alerts"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if resolved is not None:
                cursor.execute('''
                SELECT * FROM alerts WHERE resolved = ? ORDER BY timestamp DESC
                ''', (1 if resolved else 0,))
            else:
                cursor.execute('''
                SELECT * FROM alerts ORDER BY timestamp DESC
                ''')
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total transactions
            cursor.execute("SELECT COUNT(*) FROM transactions")
            total_txns = cursor.fetchone()[0]
            
            # Fraud count
            cursor.execute("SELECT COUNT(*) FROM transactions WHERE is_fraud = 1")
            fraud_count = cursor.fetchone()[0]
            
            # Today's transactions
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
            SELECT COUNT(*) FROM transactions 
            WHERE timestamp LIKE ?
            ''', (f'{today}%',))
            today_txns = cursor.fetchone()[0]
            
            # Avg risk score
            cursor.execute("SELECT AVG(risk_score) FROM transactions")
            avg_risk = cursor.fetchone()[0] or 0
            
            return {
                "total_transactions": total_txns,
                "fraud_count": fraud_count,
                "fraud_percentage": (fraud_count / total_txns * 100) if total_txns > 0 else 0,
                "today_transactions": today_txns,
                "average_risk_score": round(avg_risk, 2),
                "active_alerts": len(self.get_alerts(resolved=False))
            }

# Create global database instance
db = Database()
