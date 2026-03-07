"""
Database module for iRMC SecureAI
Using werkzeug.security - pure Python, no compilation needed!
"""

import sqlite3
import pandas as pd
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

class Database:
    def __init__(self, db_path="irmc_secureai.db"):
        self.db_path = db_path
        self.init_database()
        print("✅ Database initialized with werkzeug security")
    
    def init_database(self):
        """Initialize users table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
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
        
        # Check if any user exists
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Create default admin
            password_hash = generate_password_hash("Admin@123")
            cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role, department)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', ("admin", "admin@irmc.com", password_hash, "System Administrator", "admin", "IT"))
            
            # Create a demo analyst
            password_hash2 = generate_password_hash("demo123")
            cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role, department)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', ("analyst", "analyst@irmc.com", password_hash2, "Demo Analyst", "analyst", "Fraud Investigation"))
            
            print("✅ Default users created (admin/analyst)")
        
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
                conn.close()
                return {"success": False, "message": "Username or email already exists"}
            
            # Hash password using werkzeug
            password_hash = generate_password_hash(password)
            
            # Insert user
            cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role, department)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, full_name, role, department))
            
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
            
            # Verify using werkzeug
            if check_password_hash(password_hash, password):
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
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
            SELECT id, username, email, full_name, role, department, created_at, last_login
            FROM users WHERE id = ?
            ''', (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "id": result[0],
                    "username": result[1],
                    "email": result[2],
                    "full_name": result[3],
                    "role": result[4],
                    "department": result[5],
                    "created_at": result[6],
                    "last_login": result[7]
                }
            return None
        except:
            return None

# Create global database instance
db = Database()
