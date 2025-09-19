# Database module with security and performance issues

import sqlite3
import time

# SECURITY ISSUE: Hardcoded database credentials
DB_HOST = "localhost"
DB_USER = "admin"
DB_PASSWORD = "password123"
DB_NAME = "production_db"

class DatabaseManager:
    def __init__(self):
        self.connection = None
    
    # SECURITY ISSUE: SQL Injection vulnerability
    def get_user_by_id(self, user_id):
        query = f"SELECT * FROM users WHERE id = {user_id}"
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchone()
    
    # SECURITY ISSUE: No input sanitization
    def search_users(self, search_term):
        query = f"SELECT * FROM users WHERE name LIKE '%{search_term}%'"
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    
    # PERFORMANCE ISSUE: N+1 query problem
    def get_users_with_orders(self):
        users = self.get_all_users()
        result = []
        
        for user in users:
            # Separate query for each user - N+1 problem
            orders = self.get_orders_for_user(user['id'])
            user['orders'] = orders
            result.append(user)
        
        return result
    
    def get_all_users(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()
    
    def get_orders_for_user(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM orders WHERE user_id = {user_id}")
        return cursor.fetchall()
    
    # PERFORMANCE ISSUE: No connection pooling
    def execute_query(self, query):
        # Creates new connection for each query
        conn = sqlite3.connect(f"{DB_HOST}/{DB_NAME}")
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        return result
    
    # CODE QUALITY ISSUE: No error handling
    def update_user(self, user_id, data):
        query = f"UPDATE users SET name='{data['name']}', email='{data['email']}' WHERE id={user_id}"
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()

# SECURITY ISSUE: Debug mode enabled in production
DEBUG_MODE = True

if DEBUG_MODE:
    # SECURITY ISSUE: Logging sensitive information
    def log_query(query, params):
        print(f"Executing query: {query} with params: {params}")
        with open("debug.log", "a") as f:
            f.write(f"Query: {query}, Params: {params}\n")