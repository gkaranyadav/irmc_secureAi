"""
Database module for iRMC SecureAI
Handles user registration and authentication
"""

import sqlite3
import bcrypt
import pandas as pd
from datetime import datetime
import os

class Database:
    def __init__(self, db_path="irmc_secureai.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize users table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table (for both admins and analysts)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'analyst',
            department TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        ''')
        
        # Create default admin if no users exist
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Create default admin
            password_hash = bcrypt.hashpw("Admin@123".encode(), bcrypt.gensalt())
            cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role, department)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', ("admin", "admin@irmc.com", password_hash.decode(), "System Administrator", "admin", "IT"))
            print("✅ Default admin created")
        
        conn.commit()
        conn.close()
    
    def register_user(self, username, email, password, full_name, role="analyst", department=None):
        """Register a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                return {"success": False, "message": "Username or email already exists"}
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            
            # Insert user
            cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role, department)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash.decode(), full_name, role, department))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            return {"success": True, "message": "Registration successful", "user_id": user_id}
            
        except Exception as e:
            return {"success": False, "message": f"Registration failed: {str(e)}"}
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find user by username or email
            cursor.execute('''
            SELECT id, username, email, password_hash, full_name, role, department, is_active
            FROM users 
            WHERE username = ? OR email = ?
            ''', (username, username))
            
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return {"success": False, "message": "User not found"}
            
            user_id, db_username, email, password_hash, full_name, role, department, is_active = result
            
            if not is_active:
                conn.close()
                return {"success": False, "message": "Account is deactivated"}
            
            # Verify password
            if bcrypt.checkpw(password.encode(), password_hash.encode()):
                # Update last login
                cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                             (datetime.now(), user_id))
                conn.commit()
                
                user_data = {
                    "id": user_id,
                    "username": db_username,
                    "email": email,
                    "full_name": full_name,
                    "role": role,
                    "department": department,
                    "is_admin": role == "admin"
                }
                conn.close()
                return {"success": True, "message": "Login successful", "user": user_data}
            else:
                conn.close()
                return {"success": False, "message": "Invalid password"}
                
        except Exception as e:
            return {"success": False, "message": f"Authentication error: {str(e)}"}

# Create global database instance
db = Database()
