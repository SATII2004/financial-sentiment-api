#!/usr/bin/env python
"""
Test script to verify API keys are working.
Run this to make sure everything is set up correctly.
"""
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.api_clients import test_api_connections

if __name__ == "__main__":
    print("="*50)
    print("🔧 FINANCIAL SENTIMENT API - CONNECTION TEST")
    print("="*50)
    test_api_connections()
    print("="*50)