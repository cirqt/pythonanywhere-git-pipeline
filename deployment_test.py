#!/usr/bin/env python3
"""
Deployment Test File - Used to verify the PythonAnywhere Git Pipeline works correctly.

This file contains a test counter that should increment each time the deployment pipeline
successfully pulls the latest code from GitHub to PythonAnywhere.

Usage for testing:
1. Increment the test counter below
2. Commit and push to GitHub
3. Check this file on PythonAnywhere to verify the deployment worked
"""

# Test counter for deployment verification: 1
# Last updated: Initial deployment test
# Instructions: Increment the counter above each time you test the deployment

import datetime


def get_deployment_info():
    """Get information about this deployment test"""
    return {
        'test_counter': 1,
        'last_updated': 'Initial deployment test',
        'file_purpose': 'Verify PythonAnywhere Git Pipeline deployment',
        'timestamp': datetime.datetime.now().isoformat()
    }


def verify_deployment():
    """Print deployment verification information"""
    info = get_deployment_info()
    
    print("🔍 Deployment Verification")
    print("=" * 40)
    print(f"Test Counter: {info['test_counter']}")
    print(f"Last Updated: {info['last_updated']}")
    print(f"Current Time: {info['timestamp']}")
    print(f"File Purpose: {info['file_purpose']}")
    print("=" * 40)
    
    if info['test_counter'] > 0:
        print("✅ Deployment test file is present and accessible")
    else:
        print("❌ Deployment test counter not properly set")
    
    return info


if __name__ == "__main__":
    verify_deployment()
