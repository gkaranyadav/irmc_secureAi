"""
Database module for iRMC SecureAI
Pure Python implementation - NO external dependencies!
Uses hashlib which is built into Python
"""

import sqlite3
import pandas as pd
from datetime import datetime
import hashlib
import os
import binascii

class PasswordHasher:
    """Pure Python password hashing - no external dependencies!"""
    
    @staticmethod
    def hash_password(password):
        """
        Hash password using PBKDF2 with SHA256
        This is built into Python - no external libraries needed!
        """
        # Generate a random salt
        salt = os.urandom(32)
        
        # Hash the password with 100,000 iterations
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000  # Number of iterations
        )
        
        # Store as salt:key in hex format
        salt_hex = binascii.hexlify(salt).decode()
        key_hex = binascii.hexlify(key).decode()
        
        return f"{salt_hex}:{key_hex}"
    
    @staticmethod
    def verify_password(password, stored_hash):
        """
        Verify password against stored hash
        """
        try:
            # Split stored hash into salt and key
            salt_hex, key_hex = stored_hash.split(':')
            
            # Convert back to bytes
            salt = binascii.unhexlify(salt_hex)
            stored_key = binascii.unhexlify(key_hex)
            
            # Hash the provided password with the same salt
            new_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt,
                100000
            )
            
            # Compare securely
            return new_key == stored_key
            
        except Exception as e:
            print(f"Password verification error: {e}")
            return False

# Create global hasher instance
hasher = PasswordHasher()

class Database:
    def __init__(self, db_path="irmc_secureai.db"):
        self.db_path = db_path
        self.init_database()
        print("✅ Database initialized with pure Python hashing")
    
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
            admin_hash = hasher.hash_password("Admin@123")
            cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role, department)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', ("admin", "admin@irmc.com", admin_hash, "System Administrator", "admin", "IT"))
            
            # Create a demo analyst
            analyst_hash = hasher.hash_password("demo123")
            cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role, department)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', ("analyst", "analyst@irmc.com", analyst_hash, "Demo Analyst", "analyst", "Fraud Investigation"))
            
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
            
            # Hash password using our pure Python hasher
            password_hash = hasher.hash_password(password)
            
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
            
            # Verify using our pure Python hasher
            if hasher.verify_password(password, password_hash):
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
