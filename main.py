#!/usr/bin/env python3
"""
PythonAnywhere Git Pipeline

A module for executing git operations on PythonAnywhere hosting service
via their console API using credentials provided through YAML configuration.
"""

import requests
import yaml
import json
import time
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PAWCredentials:
    """PythonAnywhere credentials configuration"""
    username: str
    token: str
    host: str
    
    def __post_init__(self):
        if not self.host.startswith('http'):
            self.host = f"https://{self.host}"


class PythonAnywhereGitPipeline:
    """
    Main class for handling git operations on PythonAnywhere
    """
    
    def __init__(self, credentials: PAWCredentials):
        self.credentials = credentials
        self.api_base = f"{credentials.host}/api/v0/user/{credentials.username}"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {credentials.token}',
            'Content-Type': 'application/json'
        })
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def test_connection(self) -> bool:
        """Test connection to PythonAnywhere API"""
        try:
            response = self.session.get(f"{self.api_base}/cpu/")
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def execute_git_pull(self, project_path: str, branch: str = "main", github_token: str = None) -> Dict[str, Any]:
        """
        Execute git pull command in PythonAnywhere console
        
        Args:
            project_path: Path to the project directory on PythonAnywhere
            branch: Git branch to pull (default: main)
            github_token: GitHub personal access token for private repos
            
        Returns:
            Dictionary containing execution results
        """
        commands = [
            f"cd {project_path}"
        ]
        
        # Add GitHub token authentication if provided
        if github_token:
            commands.append(f"git config credential.helper store")
            commands.append(f"echo 'https://{github_token}@github.com' > ~/.git-credentials")
        
        commands.append(f"git pull origin {branch}")
        
        return self._execute_console_commands(commands)
    
    def execute_git_clone(self, repo_url: str, target_path: str, branch: str = "main", github_token: str = None) -> Dict[str, Any]:
        """
        Clone a git repository to PythonAnywhere
        
        Args:
            repo_url: Git repository URL
            target_path: Target path on PythonAnywhere
            branch: Git branch to clone (default: main)
            github_token: GitHub personal access token for private repos
            
        Returns:
            Dictionary containing execution results
        """
        # Modify repo URL to include token if provided
        if github_token and 'github.com' in repo_url:
            repo_url = repo_url.replace('https://github.com/', f'https://{github_token}@github.com/')
        
        commands = [
            f"git clone -b {branch} {repo_url} {target_path}"
        ]
        
        return self._execute_console_commands(commands)
    
    def execute_git_push(self, project_path: str, branch: str = "main", commit_message: str = None) -> Dict[str, Any]:
        """
        Execute git add, commit, and push commands in PythonAnywhere console
        
        Args:
            project_path: Path to the project directory on PythonAnywhere
            branch: Git branch to push to (default: main)
            commit_message: Commit message (optional, defaults to timestamp-based message)
            
        Returns:
            Dictionary containing execution results
        """
        if not commit_message:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Automated commit from PythonAnywhere - {timestamp}"
        
        commands = [
            f"cd {project_path}",
            "git add .",
            f'git commit -m "{commit_message}"',
            f"git push origin {branch}"
        ]
        
        return self._execute_console_commands(commands)
    
    def _execute_console_commands(self, commands: list) -> Dict[str, Any]:
        """
        Execute commands in PythonAnywhere console
        
        Args:
            commands: List of bash commands to execute
            
        Returns:
            Dictionary containing execution results
        """
        console_id = None
        try:
            # Create console session
            console_response = self.session.post(f"{self.api_base}/consoles/")
            if console_response.status_code != 201:
                raise Exception(f"Failed to create console: {console_response.text}")
            
            console_id = console_response.json()['id']
            self.logger.info(f"Created console session: {console_id}")
            
            # Wait for console to be ready
            self._wait_for_console_ready(console_id)
            
            results = []
            for command in commands:
                self.logger.info(f"Executing command: {command}")
                result = self._send_command_to_console(console_id, command)
                results.append(result)
                
                if result.get('error'):
                    break
            
            return {
                'success': all(not r.get('error') for r in results),
                'results': results,
                'console_id': console_id
            }
            
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'console_id': console_id
            }
        finally:
            if console_id:
                self._cleanup_console(console_id)
    
    def _wait_for_console_ready(self, console_id: int, timeout: int = 30):
        """Wait for console to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.session.get(f"{self.api_base}/consoles/{console_id}/")
            if response.status_code == 200:
                return
            time.sleep(1)
        raise Exception("Console readiness timeout")
    
    def _send_command_to_console(self, console_id: int, command: str) -> Dict[str, Any]:
        """Send command to console and get output"""
        # Send command
        send_response = self.session.post(
            f"{self.api_base}/consoles/{console_id}/send_input/",
            json={'input': command + '\n'}
        )
        
        if send_response.status_code != 200:
            return {'error': f"Failed to send command: {send_response.text}"}
        
        # Wait for output
        time.sleep(2)
        
        # Get latest output
        output_response = self.session.get(f"{self.api_base}/consoles/{console_id}/get_latest_output/")
        
        if output_response.status_code != 200:
            return {'error': f"Failed to get output: {output_response.text}"}
        
        output_data = output_response.json()
        return {
            'command': command,
            'output': output_data.get('output', ''),
            'error': None if 'error' not in output_data.get('output', '').lower() else output_data.get('output')
        }
    
    def _cleanup_console(self, console_id: int):
        """Clean up console session"""
        try:
            self.session.delete(f"{self.api_base}/consoles/{console_id}/")
            self.logger.info(f"Cleaned up console session: {console_id}")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup console {console_id}: {e}")


def load_credentials_from_yaml(yaml_path: str) -> PAWCredentials:
    """
    Load PythonAnywhere credentials from YAML file
    
    Args:
        yaml_path: Path to YAML configuration file
        
    Returns:
        PAWCredentials object
    """
    try:
        with open(yaml_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            
        paw_config = config.get('pythonanywhere', {})
        
        required_fields = ['username', 'token', 'host']
        missing_fields = [field for field in required_fields if field not in paw_config]
        
        if missing_fields:
            raise ValueError(f"Missing required fields in YAML: {missing_fields}")
        
        return PAWCredentials(
            username=paw_config['username'],
            token=paw_config['token'],
            host=paw_config['host']
        )
        
    except Exception as e:
        raise Exception(f"Failed to load credentials from {yaml_path}: {e}")


def load_credentials_from_env() -> PAWCredentials:
    """
    Load PythonAnywhere credentials from environment variables
    Useful for GitHub Actions and other CI/CD systems
    
    Required environment variables:
    - PAW_USERNAME: PythonAnywhere username
    - PAW_TOKEN: PythonAnywhere API token  
    - PAW_HOST: PythonAnywhere host/domain
    
    Returns:
        PAWCredentials object
    """
    import os
    
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
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return PAWCredentials(username=username, token=token, host=host)


def load_credentials(yaml_path: str = None, use_env: bool = False) -> PAWCredentials:
    """
    Load credentials from either YAML file or environment variables
    
    Args:
        yaml_path: Path to YAML configuration file (optional if use_env=True)
        use_env: If True, load from environment variables instead of YAML
        
    Returns:
        PAWCredentials object
    """
    if use_env:
        return load_credentials_from_env()
    elif yaml_path:
        return load_credentials_from_yaml(yaml_path)
    else:
        # Try environment first, then fall back to default config.yaml
        try:
            return load_credentials_from_env()
        except ValueError:
            return load_credentials_from_yaml('config.yaml')


def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PythonAnywhere Git Pipeline')
    parser.add_argument('--config', '-c', required=True, help='Path to YAML configuration file')
    parser.add_argument('--project-path', '-p', required=True, help='Project path on PythonAnywhere')
    parser.add_argument('--branch', '-b', default='main', help='Git branch (default: main)')
    parser.add_argument('--operation', '-o', choices=['pull', 'clone', 'push'], default='pull', help='Git operation')
    parser.add_argument('--repo-url', '-r', help='Repository URL (required for clone operation)')
    parser.add_argument('--commit-message', '-m', help='Commit message (for push operation)')
    
    args = parser.parse_args()
    
    try:
        # Load credentials
        credentials = load_credentials_from_yaml(args.config)
        
        # Initialize pipeline
        pipeline = PythonAnywhereGitPipeline(credentials)
        
        # Test connection
        if not pipeline.test_connection():
            print("❌ Failed to connect to PythonAnywhere API")
            return 1
        
        print("✅ Connected to PythonAnywhere API")
        
        # Execute operation
        if args.operation == 'pull':
            result = pipeline.execute_git_pull(args.project_path, args.branch)
        elif args.operation == 'clone':
            if not args.repo_url:
                print("❌ Repository URL is required for clone operation")
                return 1
            result = pipeline.execute_git_clone(args.repo_url, args.project_path, args.branch)
        elif args.operation == 'push':
            result = pipeline.execute_git_push(args.project_path, args.branch, args.commit_message)
        
        # Display results
        if result['success']:
            print("✅ Git operation completed successfully")
            for cmd_result in result['results']:
                print(f"Command: {cmd_result['command']}")
                print(f"Output: {cmd_result['output']}")
        else:
            print("❌ Git operation failed")
            if 'error' in result:
                print(f"Error: {result['error']}")
            
        return 0 if result['success'] else 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())