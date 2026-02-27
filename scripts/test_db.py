#!/usr/bin/env python
"""
Test script to verify database connection.
"""
import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("="*50)
print("🔧 TESTING DATABASE CONNECTION")
print("="*50)

try:
    # Connect to MySQL
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    
    cursor = conn.cursor()
    
    # Test query - count companies
    cursor.execute("SELECT COUNT(*) FROM companies")
    count = cursor.fetchone()[0]
    print(f"✅ Successfully connected to database!")
    print(f"📊 Found {count} companies in database")
    
    # Show all companies
    cursor.execute("SELECT ticker, company_name FROM companies")
    companies = cursor.fetchall()
    print("\n📈 Companies in database:")
    for ticker, name in companies:
        print(f"   • {ticker}: {name}")
    
    # Check other tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"\n📋 Tables in database:")
    for table in tables:
        print(f"   • {table[0]}")
    
    cursor.close()
    conn.close()
    print("\n✅ Database test completed successfully!")
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("\n🔍 Troubleshooting tips:")
    print("   1. Check if MySQL is running")
    print("   2. Verify credentials in .env file")
    print("   3. Make sure database 'sentiment_api' exists")

print("="*50)