#!/usr/bin/env python3
"""
GitHub Actions integration for PythonAnywhere Git Pipeline
Uses GitHub Secrets for secure credential management
"""

import os
import sys
from main import PythonAnywhereGitPipeline, PAWCredentials


def load_credentials_from_env() -> PAWCredentials:
    """
    Load PythonAnywhere credentials from environment variables (GitHub Secrets)
    
    Required environment variables:
    - PAW_USERNAME: PythonAnywhere username
    - PAW_TOKEN: PythonAnywhere API token
    - PAW_HOST: PythonAnywhere host/domain
    
    Returns:
        PAWCredentials object
    """
    username = os.getenv('PAW_USERNAME')
    token = os.getenv('PAW_TOKEN')
    host = os.getenv('PAW_HOST')
    
    missing_vars = []
    if not username:
        missing_vars.append('PAW_USERNAME')
    if not token:
        missing_vars.append('PAW_TOKEN')
    if not host:
        missing_vars.append('PAW_HOST')
    
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these GitHub Secrets in your repository:")
        print("   - PAW_USERNAME: Your PythonAnywhere username")
        print("   - PAW_TOKEN: Your PythonAnywhere API token")
        print("   - PAW_HOST: Your domain (e.g., username.pythonanywhere.com)")
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    print(f"Loaded credentials for user: {username}")
    print(f"Using domain: {host}")
    
    return PAWCredentials(username=username, token=token, host=host)


def deploy_to_pythonanywhere(project_path: str, branch: str = "main") -> bool:
    """
    Deploy project to PythonAnywhere using GitHub Secrets
    
    Args:
        project_path: Path to project on PythonAnywhere
        branch: Git branch to deploy
        
    Returns:
        True if deployment successful, False otherwise
    """
    try:
        # Load credentials from environment (GitHub Secrets)
        credentials = load_credentials_from_env()
        
        # Get GitHub token if available
        github_token = os.getenv('GIT_TOKEN')
        if github_token:
            print("GitHub token found for private repo access")
        else:
            print("No GitHub token found - assuming public repo")
        
        # Initialize pipeline
        pipeline = PythonAnywhereGitPipeline(credentials)
        
        # Test connection
        print("Testing connection to PythonAnywhere...")
        if not pipeline.test_connection():
            print("Failed to connect to PythonAnywhere API")
            print("Possible issues:")
            print("  1. Invalid PAW_TOKEN - check your API token")
            print("  2. Incorrect PAW_USERNAME")
            print("  3. Network connectivity issues")
            print("  4. PythonAnywhere API endpoint changes")
            print(f"  API Base URL: {pipeline.api_base}")
            return False
        
        print("Connected to PythonAnywhere API")
        
        # Execute deployment
        print(f"Deploying to {project_path} (branch: {branch})...")
        result = pipeline.execute_git_pull(project_path, branch, github_token)
        
        if result['success']:
            print("Deployment completed successfully!")
            for cmd_result in result['results']:
                if cmd_result['output'].strip():
                    print(f"   {cmd_result['output'].strip()}")
        else:
            print("Deployment failed!")
            if 'error' in result:
                print(f"   Error: {result['error']}")
            for cmd_result in result['results']:
                if cmd_result.get('error'):
                    print(f"   Command Error: {cmd_result['error']}")
        
        return result['success']
        
    except Exception as e:
        print(f"Deployment Error: {e}")
        return False


def main():
    """Main function for GitHub Actions"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy to PythonAnywhere via GitHub Actions')
    parser.add_argument('--project-path', '-p', required=True, 
                       help='Project path on PythonAnywhere')
    parser.add_argument('--branch', '-b', default='main', 
                       help='Git branch to deploy (default: main)')
    
    args = parser.parse_args()
    
    # Deploy using GitHub Secrets
    success = deploy_to_pythonanywhere(args.project_path, args.branch)
    
    if success:
        print("GitHub Actions deployment completed successfully!")
        sys.exit(0)
    else:
        print("GitHub Actions deployment failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
