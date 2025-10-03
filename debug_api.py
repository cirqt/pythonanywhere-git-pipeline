#!/usr/bin/env python3
"""
Debug script to test PythonAnywhere API connection
"""

import os
import requests
from github_deploy import load_credentials_from_env

def test_api_endpoints():
    """Test various PythonAnywhere API endpoints"""
    try:
        credentials = load_credentials_from_env()
        
        username = credentials['username']
        token = credentials['token']
        host = credentials['host']
        
        if not host.startswith('http'):
            host = f"https://{host}"
        
        # Fix API URL format - PythonAnywhere uses www.pythonanywhere.com for API
        if 'pythonanywhere.com' in host:
            api_base = f"https://www.pythonanywhere.com/api/v0/user/{username}"
        else:
            api_base = f"{host}/api/v0/user/{username}"
        
        headers = {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        }
        
        print(f"Testing API connection to: {api_base}")
        print(f"Username: {username}")
        print(f"Host: {host}")
        print("=" * 50)
        
        # Test different endpoints
        endpoints = [
            "/consoles/",
            "/cpu/",
            "/files/path/home/{}/".format(username),
        ]
        
        for endpoint in endpoints:
            url = api_base + endpoint
            print(f"Testing: {url}")
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                print(f"  Status Code: {response.status_code}")
                if response.status_code != 200:
                    print(f"  Error Response: {response.text[:200]}...")
                else:
                    print("  SUCCESS!")
                    
            except Exception as e:
                print(f"  Exception: {e}")
            
            print()
            
    except Exception as e:
        print(f"Setup error: {e}")

if __name__ == "__main__":
    test_api_endpoints()
