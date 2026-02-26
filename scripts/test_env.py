#!/usr/bin/env python
"""
Test script to check if .env file is being read correctly.
"""
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

print("="*50)
print("🔧 TESTING .ENV FILE")
print("="*50)

# Check if keys are loaded
finnhub_key = os.getenv('FINNHUB_KEY')
alpha_key = os.getenv('ALPHA_VANTAGE_KEY')

print(f"FINNHUB_KEY: {'✅ Found' if finnhub_key else '❌ Not found'}")
if finnhub_key:
    print(f"  Value: {finnhub_key[:5]}... (length: {len(finnhub_key)})")

print(f"ALPHA_VANTAGE_KEY: {'✅ Found' if alpha_key else '❌ Not found'}")
if alpha_key:
    print(f"  Value: {alpha_key[:5]}... (length: {len(alpha_key)})")

print("\n📊 Database Settings:")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_PORT: {os.getenv('DB_PORT')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_PASSWORD: {'✅ Set' if os.getenv('DB_PASSWORD') else '❌ Not set'}")
print(f"DB_NAME: {os.getenv('DB_NAME')}")

print("\n⚙️ API Settings:")
print(f"API_PORT: {os.getenv('API_PORT')}")
print(f"API_HOST: {os.getenv('API_HOST')}")
print(f"API_DEBUG: {os.getenv('API_DEBUG')}")

print("="*50)