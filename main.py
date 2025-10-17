#!/usr/bin/env python3
"""
PythonAnywhere Git Pipeline

A simplified module for executing git operations on PythonAnywhere hosting service
via their console API using always-open consoles (PAW_CLI approach).

IMPORTANT: This module requires the PAW_CLI environment variable to be set
to a console ID of an always-open console in your PythonAnywhere dashboard.
This approach is much more reliable than programmatic console creation.

Setup:
1. Run: python test_deployment.py consoles
2. Open a console in PythonAnywhere dashboard and keep it open
3. Set: export PAW_CLI=<console_id>
4. Deploy reliably without browser activation issues!
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
    password: Optional[str] = None  # Optional web password for console activation
    
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
        import os
        
        # Reset environment and navigate to home directory first
        reset_command = f"cd ~ && pwd"
        # Test if path exists and navigate to project
        test_command = f"cd {project_path} && pwd && ls -la"
        
        # Check for Git credentials from environment variables
        git_username = os.getenv('GIT_USERNAME')
        git_token = os.getenv('GIT_TOKEN')
        
        commands = [reset_command, test_command]
        
        if git_username and git_token:
            # Configure git credentials for private repositories
            self.logger.info("Configuring Git credentials for private repository access")
            config_command = f"cd {project_path} && git config credential.helper store && echo 'https://{git_username}:{git_token}@github.com' > ~/.git-credentials"
            commands.append(config_command)
            git_command = f"cd {project_path} && git pull origin {branch}"
        else:
            # No credentials provided, try without authentication (for public repos)
            self.logger.info("No Git credentials provided - attempting public repository access")
            git_command = f"cd {project_path} && git pull origin {branch}"
        
        commands.append(git_command)
        
        self.logger.info(f"Resetting directory: {reset_command}")
        self.logger.info(f"Testing path: {test_command}")
        if git_username and git_token:
            self.logger.info("Configuring Git credentials")
        self.logger.info(f"Git command: {git_command}")
        
        return self._execute_console_commands(commands)
    
    def _execute_console_commands(self, commands: list) -> Dict[str, Any]:
        """
        Execute commands in PythonAnywhere console
        
        Args:
            commands: List of bash commands to execute
            
        Returns:
            Dictionary containing execution results
        """
        import os
        
        console_id = None
        try:
            # Check if we have a pre-existing console ID from environment variable
            existing_console_id = os.getenv('PAW_CLI')
            
            if existing_console_id:
                # Use the existing console - this is the preferred method
                console_id = int(existing_console_id)
                self.logger.info(f"Using pre-existing console session: {console_id}")
                self.logger.info("Using PAW_CLI console - attempting web activation if needed")
                
                # Proactively try to activate the console via web visit
                # This is our new enhancement!
                self.logger.info("Proactively activating console via web page visit...")
                activation_success = self._activate_console_via_web(console_id)
                if activation_success:
                    self.logger.info("Console web activation successful")
                else:
                    self.logger.warning("Console web activation failed, but continuing anyway")
                
            else:
                # PAW_CLI not set - inform user of better approach
                self.logger.error("PAW_CLI environment variable not set!")
                self.logger.error("For reliable deployments, please:")
                self.logger.error("1. Run: python test_deployment.py consoles")
                self.logger.error("2. Open PythonAnywhere dashboard and click on a console")
                self.logger.error("3. Set: export PAW_CLI=<console_id>")
                self.logger.error("4. Re-run your deployment")
                raise Exception("PAW_CLI not configured - please set up always-open console")
            
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
    
    def _activate_console_via_web(self, console_id: int) -> bool:
        """
        Activate console by authenticating with web interface and visiting console page
        This requires username/password authentication to create a session, then visits the console
        
        Args:
            console_id: The console ID to activate
            
        Returns:
            bool: True if activation appears successful, False otherwise
        """
        try:
            # Check if we have web credentials
            if not self.credentials.password:
                self.logger.warning("No web password provided - cannot authenticate with web interface")
                self.logger.info("Testing if console is already accessible via API...")
                test_response = self.session.get(f"{self.api_base}/consoles/{console_id}/")
                return test_response.status_code == 200
            
            # Determine the correct base URL
            if 'eu.pythonanywhere.com' in self.api_base:
                base_url = "https://eu.pythonanywhere.com"
            else:
                base_url = "https://www.pythonanywhere.com"
            
            self.logger.info(f"Attempting web authentication for console activation...")
            
            # Create a web session to maintain cookies
            web_session = requests.Session()
            web_session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            # Step 1: Get login page to retrieve CSRF token
            login_url = f"{base_url}/login/"
            self.logger.info(f"Getting login page: {login_url}")
            login_page = web_session.get(login_url, timeout=10)
            
            if login_page.status_code != 200:
                self.logger.warning(f"Failed to get login page (status: {login_page.status_code})")
                return False
            
            # Extract CSRF token from login page
            import re
            csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', login_page.text)
            if not csrf_match:
                self.logger.warning("Could not find CSRF token in login page")
                return False
            
            csrf_token = csrf_match.group(1)
            self.logger.info("Successfully extracted CSRF token")
            
            # Step 2: Perform login
            login_data = {
                'csrfmiddlewaretoken': csrf_token,
                'auth-username': self.credentials.username,
                'auth-password': self.credentials.password,
                'view-login': 'Log in',
            }
            
            web_session.headers.update({
                'Referer': login_url,
                'Content-Type': 'application/x-www-form-urlencoded',
            })
            
            self.logger.info("Attempting to log in...")
            login_response = web_session.post(login_url, data=login_data, timeout=10)
            
            # Check if login was successful (should redirect or show dashboard)
            if login_response.status_code == 200 and 'login' in login_response.url.lower():
                self.logger.warning("Login appears to have failed - still on login page")
                return False
            
            self.logger.info(f"Login response status: {login_response.status_code}")
            self.logger.info("Login appears successful, visiting console page...")
            
            # Step 3: Visit console page to activate it
            console_url = f"{base_url}/user/{self.credentials.username}/consoles/{console_id}/"
            self.logger.info(f"Visiting console page: {console_url}")
            
            console_response = web_session.get(console_url, timeout=10)
            
            if console_response.status_code == 200:
                self.logger.info("Successfully visited console page")
                
                # Give the console a moment to initialize
                self.logger.info("Waiting 15 seconds for console to initialize...")
                time.sleep(15)
                
                # Test if console is now responsive via API
                test_response = self.session.get(f"{self.api_base}/consoles/{console_id}/")
                if test_response.status_code == 200:
                    self.logger.info(f"Console {console_id} is now accessible via API")
                    return True
                else:
                    self.logger.warning(f"Console page visit successful but API still not accessible: {test_response.status_code}")
                    return False
            else:
                self.logger.warning(f"Failed to visit console page (status: {console_response.status_code})")
                return False
                
        except requests.exceptions.Timeout:
            self.logger.warning("Timeout during web authentication")
            return False
        except Exception as e:
            self.logger.warning(f"Failed to activate console via web authentication: {e}")
            return False
    
    def _send_command_to_console(self, console_id: int, command: str) -> Dict[str, Any]:
        """Send command to console and get output"""
        self.logger.info(f"=== SENDING COMMAND TO CONSOLE {console_id} ===")
        self.logger.info(f"Command: {command}")
        self.logger.info(f"API endpoint: {self.api_base}/consoles/{console_id}/send_input/")
        
        # Send command
        send_response = self.session.post(
            f"{self.api_base}/consoles/{console_id}/send_input/",
            json={'input': command + '\n'}
        )
        
        self.logger.info(f"Send response status: {send_response.status_code}")
        self.logger.info(f"Send response text: {send_response.text}")
        
        if send_response.status_code != 200:
            error_msg = send_response.text
            # If console still not started, try activating it via web page visit
            if "Console not yet started" in error_msg:
                self.logger.warning(f"Console {console_id} not started, attempting web activation...")
                if self._activate_console_via_web(console_id):
                    self.logger.info(f"Console {console_id} activated, retrying command...")
                    # Retry the command once
                    send_response = self.session.post(
                        f"{self.api_base}/consoles/{console_id}/send_input/",
                        json={'input': command + '\n'}
                    )
                    if send_response.status_code != 200:
                        return {'error': f"Failed to send command after web activation: {send_response.text}"}
                else:
                    return {
                        'error': f"Console {console_id} not started and web activation failed. "
                                 f"Please manually open the console in your PythonAnywhere dashboard, then set PAW_CLI={console_id}"
                    }
            else:
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


def load_credentials(yaml_path: str = None) -> PAWCredentials:
    """
    Load PythonAnywhere credentials with automatic hierarchy:
    1. Try environment variables first (for GitHub Actions/CI/CD)
    2. Fall back to YAML file if explicitly specified
    
    Args:
        yaml_path: Path to YAML configuration file (required for local development)
        
    Returns:
        PAWCredentials object
    """
    import os
    
    # Try environment variables first (GitHub Actions will populate these)
    username = os.getenv('PAW_USERNAME')
    token = os.getenv('PAW_TOKEN') 
    host = os.getenv('PAW_HOST')
    
    if username and token and host:
        # Environment variables found - use them (GitHub Actions scenario)
        console_id = os.getenv('PAW_CLI')
        if not console_id:
            print("WARNING: PAW_CLI not set!")
            print("For reliable deployments, please:")
            print("1. Run: python test_deployment.py consoles") 
            print("2. Open a console in PythonAnywhere dashboard")
            print("3. Set PAW_CLI secret in GitHub repository")
            print("Deployments may fail without PAW_CLI!")
            
        return PAWCredentials(username=username, token=token, host=host)
    
    # No environment variables - YAML file must be provided for local development
    if not yaml_path:
        raise Exception(
            "No environment variables found and no YAML file specified.\n"
            "For GitHub Actions: Set PAW_USERNAME, PAW_TOKEN, PAW_HOST secrets\n"
            "For local development: Use --config path/to/your/config.yaml"
        )
    
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
            host=paw_config['host'],
            password=paw_config.get('password')  # Optional web password
        )
        
    except FileNotFoundError:
        raise Exception(f"YAML file '{yaml_path}' not found")
    except Exception as e:
        raise Exception(f"Failed to load credentials from {yaml_path}: {e}")

def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PythonAnywhere Git Pipeline')
    parser.add_argument('--config', '-c', required=True, help='Path to YAML configuration file')
    parser.add_argument('--project-path', '-p', required=True, help='Project path on PythonAnywhere')
    parser.add_argument('--branch', '-b', default='main', help='Git branch (default: main)')
    parser.add_argument('--operation', '-o', choices=['pull', 'push'], default='pull', help='Git operation')
    parser.add_argument('--commit-message', '-m', help='Commit message (for push operation)')
    
    args = parser.parse_args()
    
    try:
        # Load credentials using smart hierarchy
        credentials = load_credentials(args.config)
        
        # Initialize pipeline
        pipeline = PythonAnywhereGitPipeline(credentials)
        
        # Test connection
        if not pipeline.test_connection():
            print("Failed to connect to PythonAnywhere API")
            return 1
        
        print("Connected to PythonAnywhere API")
        
        # Execute operation
        if args.operation == 'pull':
            result = pipeline.execute_git_pull(args.project_path, args.branch)
        elif args.operation == 'push':
            result = pipeline.execute_git_push(args.project_path, args.branch, args.commit_message)
        
        # Display results
        if result['success']:
            print("Git operation completed successfully")
            for cmd_result in result['results']:
                print(f"Command: {cmd_result['command']}")
                print(f"Output: {cmd_result['output']}")
        else:
            print("Git operation failed")
            if 'error' in result:
                print(f"Error: {result['error']}")
            
        return 0 if result['success'] else 1
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())