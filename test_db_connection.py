#!/usr/bin/env python
"""
Test script to verify database connection
"""
import os
import sys
import time
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test connecting to the database using psycopg2 directly"""
    print("Testing database connection...")
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Parse the URL
    parsed = urlparse(database_url)
    dbname = parsed.path[1:]
    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port
    
    print(f"Attempting to connect to: {host}:{port} as {user}")
    
    # Try to connect
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            connect_timeout=10,
            sslmode='require'
        )
        
        print("Connection successful!")
        
        # Test a simple query
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(f"PostgreSQL version: {version[0]}")
            
            # Try to get users table info
            try:
                cur.execute("SELECT COUNT(*) FROM accounts_customuser;")
                user_count = cur.fetchone()
                print(f"User count: {user_count[0]}")
            except Exception as e:
                print(f"Error querying users table: {e}")
        
        conn.close()
        return True
    
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    # Try multiple times with delay
    for attempt in range(1, 4):
        print(f"\nAttempt {attempt}/3")
        if test_connection():
            print("\nDatabase connection test: SUCCESS")
            sys.exit(0)
        
        if attempt < 3:
            print(f"Retrying in 5 seconds...")
            time.sleep(5)
    
    print("\nDatabase connection test: FAILED")
    sys.exit(1) 