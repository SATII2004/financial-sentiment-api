#!/usr/bin/env python
"""
Test script to verify database models are working
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal, Company
from sqlalchemy import text

print("="*50)
print("🔧 TESTING DATABASE MODELS")
print("="*50)

try:
    # Create session
    db = SessionLocal()
    
    # Test raw SQL query
    result = db.execute(text("SELECT COUNT(*) FROM companies"))
    count = result.scalar()
    print(f"✅ Connected to database successfully!")
    print(f"📊 Found {count} companies")
    
    # Test ORM query
    companies = db.query(Company).all()
    print("\n📈 Companies from ORM:")
    for company in companies:
        print(f"   • {company.ticker}: {company.company_name} (ID: {company.id})")
    
    db.close()
    print("\n✅ Model tests completed successfully!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")

print("="*50)