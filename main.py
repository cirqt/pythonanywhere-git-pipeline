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
        
        # Reset environment and build command sequence that runs in the project directory
        reset_command = "cd ~ && pwd"
        
        command_parts = [
            f"cd {project_path}",
            "git add .",
            f'git commit -m "{commit_message}"',
            f"git push origin {branch}"
        ]
        
        # Join all commands with && to ensure they run in sequence in the same directory
        full_command = " && ".join(command_parts)
        
        return self._execute_console_commands([reset_command, full_command])
    
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
                self.logger.info("Using PAW_CLI console - no creation or initialization needed")
                
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
    
    # DEPRECATED: Console initialization no longer needed with PAW_CLI approach
    # Keep for backward compatibility, but PAW_CLI is the preferred method
    def _initialize_console(self, console_id: int, timeout: int = 120):
        """
        DEPRECATED: Use PAW_CLI environment variable instead
        
        Initialize console by attempting to start it through API interactions
        PythonAnywhere requires console to be accessed in browser first, but we can try
        multiple approaches to wake it up programmatically.
        """
        self.logger.warning("_initialize_console is deprecated - use PAW_CLI instead")
        self.logger.info(f"Attempting to initialize console {console_id}...")
        start_time = time.time()
        
        # Try different initialization strategies
        strategies = [
            ("echo test", "Basic echo command"),
            ("pwd", "Print working directory"), 
            ("whoami", "Check user"),
            ("ls", "List directory"),
            ("bash --version", "Check bash version")
        ]
        
        for attempt, (cmd, desc) in enumerate(strategies):
            if time.time() - start_time > timeout:
                break
                
            try:
                self.logger.info(f"Initialization attempt {attempt + 1}: {desc}")
                
                # Send initialization command
                init_response = self.session.post(
                    f"{self.api_base}/consoles/{console_id}/send_input/",
                    json={'input': f'{cmd}\n'}
                )
                
                if init_response.status_code == 200:
                    self.logger.info(f"Console {console_id} accepted command: {cmd}")
                    
                    # Wait for output (increased for slower consoles)
                    time.sleep(5)
                    
                    # Check for output
                    output_response = self.session.get(f"{self.api_base}/consoles/{console_id}/get_latest_output/")
                    if output_response.status_code == 200:
                        output_data = output_response.json()
                        output_text = output_data.get('output', '')
                        
                        if output_text.strip():
                            self.logger.info(f"Console {console_id} is responding with output: {output_text[:100]}")
                            return True
                        else:
                            self.logger.info(f"Console {console_id} command sent but no output yet...")
                            
                elif "Console not yet started" in init_response.text:
                    self.logger.info(f"Console {console_id} still not started, trying next strategy...")
                else:
                    self.logger.warning(f"Unexpected response for console {console_id}: {init_response.status_code} - {init_response.text[:100]}")
                    
            except Exception as e:
                self.logger.info(f"Console {console_id} initialization attempt {attempt + 1} failed: {e}")
            
            time.sleep(5)  # Wait between attempts
        
        # If we get here, the console never responded properly
        self.logger.warning(f"Console {console_id} initialization attempts exhausted. This may be due to PythonAnywhere requiring browser access to start consoles.")
        return False

    def _wait_for_console_ready(self, console_id: int, timeout: int = 30):
        """Wait for console to be ready"""
        start_time = time.time()
        
        self.logger.info(f"Warming up console {console_id}...")
        
        while time.time() - start_time < timeout:
            try:
                # First, check console status
                status_response = self.session.get(f"{self.api_base}/consoles/{console_id}/")
                if status_response.status_code == 200:
                    self.logger.info(f"Console {console_id} status OK")
                    
                    # Try to get latest output to fully initialize the console
                    output_response = self.session.get(f"{self.api_base}/consoles/{console_id}/get_latest_output/")
                    if output_response.status_code == 200:
                        self.logger.info(f"Console {console_id} is fully ready")
                        return
                    else:
                        self.logger.info(f"Console {console_id} still warming up... (output endpoint: {output_response.status_code})")
                        
                else:
                    self.logger.info(f"Console {console_id} status not ready: {status_response.status_code}")
                    
            except Exception as e:
                self.logger.info(f"Console {console_id} not ready yet: {e}")
            
            time.sleep(3)  # Wait a bit longer between checks
        
        raise Exception(f"Console {console_id} readiness timeout after {timeout} seconds")
    
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
            # If console still not started, give it one more chance
            if "Console not yet started" in error_msg:
                self.logger.warning(f"Console {console_id} not started, reinitializing...")
                try:
                    self._initialize_console(console_id, timeout=30)
                    # Retry once
                    send_response = self.session.post(
                        f"{self.api_base}/consoles/{console_id}/send_input/",
                        json={'input': command + '\n'}
                    )
                    if send_response.status_code != 200:
                        return {'error': f"Failed to send command after reinit: {send_response.text}"}
                except Exception as e:
                    return {'error': f"Console reinitialization failed: {e}"}
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
    
    # DEPRECATED: Console cleanup no longer needed with PAW_CLI approach
    # Keep for backward compatibility, but PAW_CLI consoles should stay open
    def _cleanup_console(self, console_id: int):
        """
        DEPRECATED: Use PAW_CLI environment variable instead
        
        Clean up console session - not recommended when using PAW_CLI
        """
        self.logger.warning("_cleanup_console is deprecated - PAW_CLI consoles should stay open")
        try:
            self.session.delete(f"{self.api_base}/consoles/{console_id}/")
            self.logger.info(f"Cleaned up console session: {console_id}")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup console {console_id}: {e}")
    
    def list_available_consoles(self) -> Dict[str, Any]:
        """
        List all available console sessions for the user
        Useful for finding console IDs to use with PAW_CLI environment variable
        
        Returns:
            Dictionary containing list of console sessions with their IDs and status
        """
        try:
            response = self.session.get(f"{self.api_base}/consoles/")
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"Failed to list consoles: {response.text}"
                }
            
            consoles = response.json()
            self.logger.info(f"Found {len(consoles)} console sessions:")
            
            for console in consoles:
                console_id = console.get('id', 'Unknown')
                executable = console.get('executable', 'Unknown')
                self.logger.info(f"  Console ID: {console_id} (executable: {executable})")
            
            return {
                'success': True,
                'consoles': consoles,
                'count': len(consoles)
            }
            
        except Exception as e:
            error_msg = f"Failed to list consoles: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }


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
    Recommended for GitHub Actions and CI/CD systems
    
    Required environment variables:
    - PAW_USERNAME: PythonAnywhere username
    - PAW_TOKEN: PythonAnywhere API token  
    - PAW_HOST: PythonAnywhere host/domain
    - PAW_CLI: Console ID of an always-open console (HIGHLY RECOMMENDED)
    
    Returns:
        PAWCredentials object
    """
    import os
    
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
        print("WARNING: PAW_CLI not set!")
        print("For reliable deployments, please:")
        print("1. Run: python test_deployment.py consoles")
        print("2. Open a console in PythonAnywhere dashboard")  
        print("3. Set: export PAW_CLI=<console_id>")
        print("Deployments may fail without PAW_CLI!")
    
    return PAWCredentials(username=username, token=token, host=host)
    
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
    parser.add_argument('--operation', '-o', choices=['pull', 'push'], default='pull', help='Git operation')
    parser.add_argument('--commit-message', '-m', help='Commit message (for push operation)')
    
    args = parser.parse_args()
    
    try:
        # Load credentials
        credentials = load_credentials_from_yaml(args.config)
        
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