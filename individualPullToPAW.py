#!/usr/bin/env python3
"""
Simple deployment script to pull latest code to PythonAnywhere
"""

import os
import requests
import json
import time
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass


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
        
        # Setup logging first
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Fix API URL format - PythonAnywhere API documentation specifies exact hosts
        host = credentials.host.replace('https://', '').replace('http://', '').rstrip('/')
        
        if 'eu.pythonanywhere.com' in host:
            self.api_base = f"https://eu.pythonanywhere.com/api/v0/user/{credentials.username}"
            self.logger.info("Using EU PythonAnywhere API endpoint")
        elif 'pythonanywhere.com' in host:
            self.api_base = f"https://www.pythonanywhere.com/api/v0/user/{credentials.username}"
            self.logger.info("Using US PythonAnywhere API endpoint")
        else:
            # Fallback - assume US
            self.api_base = f"https://www.pythonanywhere.com/api/v0/user/{credentials.username}"
            self.logger.warning(f"Unknown host format '{host}', defaulting to US endpoint")
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {credentials.token}',
            'Content-Type': 'application/json'
        })
        
        self.logger.info(f"API Base URL: {self.api_base}")
    
    def test_connection(self) -> bool:
        """Test connection to PythonAnywhere API"""
        try:
            # Try the consoles endpoint first (more likely to be accessible)
            response = self.session.get(f"{self.api_base}/consoles/")
            if response.status_code == 200:
                return True
            
            # Fallback to cpu endpoint
            response = self.session.get(f"{self.api_base}/cpu/")
            if response.status_code == 200:
                return True
                
            # If both fail, log the error
            self.logger.error(f"API connection failed. Status: {response.status_code}, Response: {response.text}")
            return False
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def execute_git_pull(self, project_path: str, branch: str = "main") -> Dict[str, Any]:
        """
        Execute git pull command in PythonAnywhere console
        
        Args:
            project_path: Path to the project directory on PythonAnywhere
            branch: Git branch to pull (default: main)
            
        Returns:
            Dictionary containing execution results
        """
        # Reset environment and navigate to home directory first
        reset_command = f"cd ~ && pwd"
        # Test if path exists and navigate to project
        test_command = f"cd {project_path} && pwd && ls -la"
        # Execute git pull
        git_command = f"cd {project_path} && git pull origin {branch}"
        
        self.logger.info(f"Resetting directory: {reset_command}")
        self.logger.info(f"Testing path: {test_command}")
        self.logger.info(f"Git command: {git_command}")
        
        return self._execute_console_commands([reset_command, test_command, git_command])
    
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
            # Check if we have a pre-existing console ID from environment variable
            existing_console_id = os.getenv('PAW_CLI')
            
            if existing_console_id:
                # Use the existing console - this is the preferred method
                console_id = int(existing_console_id)
                self.logger.info(f"Using pre-existing console session: {console_id}")
                self.logger.info("Using PAW_CLI console - no creation or initialization needed")
                
            else:
                # PAW_CLI not set - inform user of better approach
                raise Exception("PAW_CLI not configured - please set up pre-initialized console")

            # Execute commands on the console
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
    
    def _send_command_to_console(self, console_id: int, command: str) -> Dict[str, Any]:
        """Send command to console and get output"""
        
        # Send command
        send_response = self.session.post(
            f"{self.api_base}/consoles/{console_id}/send_input/",
            json={'input': command + '\n'}
        )
        
        if send_response.status_code != 200:
            error_msg = send_response.text
            return {'error': f"Failed to send command: {error_msg}"}
        
        # Wait for command to execute (increased wait time for git operations)
        self.logger.info("Waiting 5 seconds for command execution...")
        time.sleep(5)
        
        # Get latest output
        self.logger.info(f"Getting output from: {self.api_base}/consoles/{console_id}/get_latest_output/")
        output_response = self.session.get(f"{self.api_base}/consoles/{console_id}/get_latest_output/")
        
        self.logger.info(f"Output response status: {output_response.status_code}")
        self.logger.info(f"Output response text preview: {output_response.text[:200]}...")
        
        if output_response.status_code != 200:
            return {'error': f"Failed to get output: {output_response.text}"}
        
        output_data = output_response.json()
        output_text = output_data.get('output', '')
        
        self.logger.info(f"Retrieved output length: {len(output_text)} characters")
        self.logger.info(f"Output preview: {output_text[:300] if output_text else 'NO OUTPUT'}")
        
        return {
            'command': command,
            'output': output_text,
            'error': None if not self._is_error_output(output_text) else output_text
        }
    
    def _is_error_output(self, output: str) -> bool:
        """Check if output contains error indicators"""
        if not output:
            return False
        
        error_indicators = [
            'error:', 'Error:', 'ERROR:',
            'failed:', 'Failed:', 'FAILED:',
            'fatal:', 'Fatal:', 'FATAL:',
            'permission denied',
            'command not found',
            'no such file',
            'cannot access'
        ]
        
        output_lower = output.lower()
        return any(indicator.lower() in output_lower for indicator in error_indicators)


def load_credentials_from_env() -> PAWCredentials:
    """
    Load PythonAnywhere credentials from environment variables
    Recommended for GitHub Actions and CI/CD systems
    
    Required environment variables:
    - PAW_USERNAME: PythonAnywhere username
    - PAW_TOKEN: PythonAnywhere API token  
    - PAW_HOST: PythonAnywhere host/domain
    - PAW_CLI: Console ID of an already initiated console
    
    Returns:
        PAWCredentials object
    """
    username = os.getenv('PAW_USERNAME')
    token = os.getenv('PAW_TOKEN')
    host = os.getenv('PAW_HOST')
    console_id = os.getenv('PAW_CLI')
    
    missing_vars = []
    if not username:
        missing_vars.append('PAW_USERNAME')
    if not token:
        missing_vars.append('PAW_TOKEN')
    if not host:
        missing_vars.append('PAW_HOST')
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    if not console_id:
        pass
    
    return PAWCredentials(username=username, token=token, host=host)

def deploy():
    """Deploy latest code to PythonAnywhere"""
    
    # Configuration from environment variables
    PROJECT_PATH = os.getenv('PAW_PROJECT_PATH')
    BRANCH = "main"
    
    # Validate required environment variables
    if not PROJECT_PATH:
        print("Error: PAW_PROJECT_PATH environment variable not set")
        print("Set it with: export PAW_PROJECT_PATH='/home/username/project'")
        return
    
    # Check for GitHub token (for private repos)
    git_token = os.getenv('GIT_TOKEN')
    
    try:
        # Load credentials from environment
        credentials = load_credentials_from_env()
        
        # Initialize pipeline
        pipeline = PythonAnywhereGitPipeline(credentials)
        
        # Test connection
        if not pipeline.test_connection():
            print("Failed to connect to PythonAnywhere API")
            return
        
        # Execute git pull
        print(f"Pulling latest changes from {BRANCH} branch...")
        result = pipeline.execute_git_pull(PROJECT_PATH, BRANCH)
        
        if result['success']:
            print("Deployment successful!")
        else:
            print("Deployment failed!")
            if 'error' in result:
                print(f"Error: {result['error']}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    deploy()