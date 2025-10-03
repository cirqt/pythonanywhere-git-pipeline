#!/usr/bin/env python3
"""
Enhanced Error Handling for PythonAnywhere Git Pipeline
"""

import os
import sys
from pathlib import Path
from main import load_credentials_from_yaml, load_credentials_from_env, PythonAnywhereGitPipeline


class PipelineConfigError(Exception):
    """Custom exception for configuration errors"""
    pass


class PipelineConnectionError(Exception):
    """Custom exception for connection errors"""
    pass


class PipelineExecutionError(Exception):
    """Custom exception for execution errors"""
    pass


def validate_yaml_config(yaml_path: str) -> dict:
    """
    Validate YAML configuration with detailed error messages
    
    Args:
        yaml_path: Path to YAML configuration file
        
    Returns:
        Dictionary with validation results
        
    Raises:
        PipelineConfigError: If configuration is invalid
    """
    if not Path(yaml_path).exists():
        raise PipelineConfigError(
            f"❌ Configuration file not found: {yaml_path}\n"
            f"   💡 Create it by copying config.yaml.example:\n"
            f"   cp config.yaml.example config.yaml"
        )
    
    try:
        import yaml
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise PipelineConfigError(f"❌ Invalid YAML syntax in {yaml_path}: {e}")
    except Exception as e:
        raise PipelineConfigError(f"❌ Cannot read {yaml_path}: {e}")
    
    if not config:
        raise PipelineConfigError(f"❌ Empty configuration file: {yaml_path}")
    
    if 'pythonanywhere' not in config:
        raise PipelineConfigError(
            f"❌ Missing 'pythonanywhere' section in {yaml_path}\n"
            f"   💡 Required structure:\n"
            f"   pythonanywhere:\n"
            f"     username: 'your_username'\n"
            f"     token: 'your_token'\n"
            f"     host: 'your_host.pythonanywhere.com'"
        )
    
    paw_config = config['pythonanywhere']
    required_fields = ['username', 'token', 'host']
    missing_fields = []
    empty_fields = []
    
    for field in required_fields:
        if field not in paw_config:
            missing_fields.append(field)
        elif not paw_config[field] or paw_config[field].strip() == "" or "your_" in paw_config[field]:
            empty_fields.append(field)
    
    if missing_fields:
        raise PipelineConfigError(
            f"❌ Missing required fields in {yaml_path}: {missing_fields}\n"
            f"   💡 Add these fields to the 'pythonanywhere' section"
        )
    
    if empty_fields:
        raise PipelineConfigError(
            f"❌ Empty or placeholder values in {yaml_path}: {empty_fields}\n"
            f"   💡 Replace placeholder values with your actual credentials:\n"
            f"   - username: Your PythonAnywhere username\n"
            f"   - token: Get from https://www.pythonanywhere.com/account/#api_token\n"
            f"   - host: Usually 'yourusername.pythonanywhere.com'"
        )
    
    return {
        'valid': True,
        'config': config,
        'message': '✅ Configuration file is valid'
    }


def validate_env_config() -> dict:
    """
    Validate environment variable configuration
    
    Returns:
        Dictionary with validation results
        
    Raises:
        PipelineConfigError: If environment variables are invalid
    """
    required_vars = ['PAW_USERNAME', 'PAW_TOKEN', 'PAW_HOST']
    missing_vars = []
    empty_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif value.strip() == "" or "your_" in value.lower():
            empty_vars.append(var)
    
    if missing_vars:
        raise PipelineConfigError(
            f"❌ Missing required environment variables: {missing_vars}\n"
            f"   💡 Set these environment variables or GitHub Secrets:\n"
            f"   - PAW_USERNAME: Your PythonAnywhere username\n"
            f"   - PAW_TOKEN: Your PythonAnywhere API token\n"
            f"   - PAW_HOST: Your PythonAnywhere domain"
        )
    
    if empty_vars:
        raise PipelineConfigError(
            f"❌ Empty or placeholder environment variables: {empty_vars}\n"
            f"   💡 Set proper values for these variables"
        )
    
    return {
        'valid': True,
        'message': '✅ Environment variables are valid'
    }


def safe_load_credentials(yaml_path: str = None, use_env: bool = False):
    """
    Safely load credentials with comprehensive error handling
    
    Args:
        yaml_path: Path to YAML file (optional)
        use_env: Whether to use environment variables
        
    Returns:
        PAWCredentials object
        
    Raises:
        PipelineConfigError: If credentials cannot be loaded
    """
    if use_env:
        print("🔍 Loading credentials from environment variables...")
        validate_env_config()
        try:
            return load_credentials_from_env()
        except Exception as e:
            raise PipelineConfigError(f"❌ Failed to load environment credentials: {e}")
    
    elif yaml_path:
        print(f"🔍 Loading credentials from {yaml_path}...")
        validate_yaml_config(yaml_path)
        try:
            return load_credentials_from_yaml(yaml_path)
        except Exception as e:
            raise PipelineConfigError(f"❌ Failed to load YAML credentials: {e}")
    
    else:
        # Auto-detect mode
        print("🔍 Auto-detecting credential source...")
        
        # Try environment first
        try:
            validate_env_config()
            print("✅ Using environment variables")
            return load_credentials_from_env()
        except PipelineConfigError:
            print("⚠️  Environment variables not available, trying config.yaml...")
        
        # Try config.yaml
        config_path = "config.yaml"
        try:
            validate_yaml_config(config_path)
            print(f"✅ Using {config_path}")
            return load_credentials_from_yaml(config_path)
        except PipelineConfigError as e:
            raise PipelineConfigError(
                f"❌ No valid credentials found!\n\n"
                f"Options:\n"
                f"1. Create config.yaml with your credentials\n"
                f"2. Set environment variables (PAW_USERNAME, PAW_TOKEN, PAW_HOST)\n"
                f"3. Use GitHub Secrets for CI/CD\n\n"
                f"Last error: {e}"
            )


def safe_test_connection(pipeline):
    """
    Safely test connection with detailed error messages
    
    Args:
        pipeline: PythonAnywhereGitPipeline instance
        
    Returns:
        Boolean indicating success
        
    Raises:
        PipelineConnectionError: If connection fails
    """
    print("🔍 Testing connection to PythonAnywhere...")
    
    try:
        if pipeline.test_connection():
            print("✅ Connection successful!")
            return True
        else:
            raise PipelineConnectionError(
                f"❌ Connection failed!\n"
                f"   💡 Possible issues:\n"
                f"   - Invalid API token\n"
                f"   - Incorrect username\n"
                f"   - Wrong host/domain\n"
                f"   - Network connectivity issues\n"
                f"   - PythonAnywhere API is down\n\n"
                f"   🔧 Troubleshooting:\n"
                f"   - Verify credentials at https://www.pythonanywhere.com/account/\n"
                f"   - Check API token is active and not expired\n"
                f"   - Ensure host format: 'username.pythonanywhere.com'"
            )
    except Exception as e:
        raise PipelineConnectionError(f"❌ Connection test error: {e}")


def safe_execute_git_operation(pipeline, operation, *args, **kwargs):
    """
    Safely execute git operations with error handling
    
    Args:
        pipeline: PythonAnywhereGitPipeline instance
        operation: Operation name ('pull', 'push', 'clone')
        *args, **kwargs: Operation arguments
        
    Returns:
        Operation result
        
    Raises:
        PipelineExecutionError: If operation fails
    """
    operation_map = {
        'pull': pipeline.execute_git_pull,
        'push': pipeline.execute_git_push,
        'clone': pipeline.execute_git_clone
    }
    
    if operation not in operation_map:
        raise PipelineExecutionError(f"❌ Unknown operation: {operation}")
    
    print(f"🚀 Executing git {operation}...")
    
    try:
        result = operation_map[operation](*args, **kwargs)
        
        if result['success']:
            print(f"✅ Git {operation} completed successfully!")
            return result
        else:
            error_details = []
            if 'error' in result:
                error_details.append(f"General error: {result['error']}")
            
            for cmd_result in result.get('results', []):
                if cmd_result.get('error'):
                    error_details.append(f"Command '{cmd_result['command']}': {cmd_result['error']}")
            
            error_msg = "\n   ".join(error_details) if error_details else "Unknown error"
            
            raise PipelineExecutionError(
                f"❌ Git {operation} failed!\n"
                f"   Details: {error_msg}\n\n"
                f"   💡 Common issues:\n"
                f"   - Project path doesn't exist on PythonAnywhere\n"
                f"   - Git repository not initialized\n"
                f"   - Permission issues\n"
                f"   - Network connectivity problems\n"
                f"   - Branch doesn't exist"
            )
    
    except Exception as e:
        if isinstance(e, PipelineExecutionError):
            raise
        raise PipelineExecutionError(f"❌ Git {operation} execution error: {e}")


def main_with_error_handling():
    """
    Main function with comprehensive error handling
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy to PythonAnywhere with enhanced error handling')
    parser.add_argument('--project-path', '-p', help='Project path on PythonAnywhere')
    parser.add_argument('--branch', '-b', default='main', help='Git branch to deploy')
    parser.add_argument('--config', '-c', help='Path to YAML configuration file')
    parser.add_argument('--use-env', action='store_true', help='Use environment variables instead of YAML')
    parser.add_argument('--operation', '-o', choices=['pull', 'push', 'clone'], default='pull', help='Git operation')
    
    args = parser.parse_args()
    
    try:
        # Load credentials safely
        if args.use_env:
            credentials = safe_load_credentials(use_env=True)
        elif args.config:
            credentials = safe_load_credentials(yaml_path=args.config)
        else:
            credentials = safe_load_credentials()
        
        # Initialize pipeline
        pipeline = PythonAnywhereGitPipeline(credentials)
        
        # Test connection safely
        safe_test_connection(pipeline)
        
        # Determine project path
        if args.project_path:
            project_path = args.project_path
        else:
            # Use default path based on username
            project_path = f"/home/{credentials.username}/pythonanywhere-git-pipeline"
        
        # Execute git operation safely
        result = safe_execute_git_operation(pipeline, args.operation, project_path, args.branch)
        
        # Show results
        for cmd_result in result.get('results', []):
            if cmd_result.get('output') and cmd_result['output'].strip():
                print(f"📄 {cmd_result['output'].strip()}")
        
        print("🎉 Pipeline executed successfully!")
        return True
        
    except PipelineConfigError as e:
        print(f"\n🔧 Configuration Error:\n{e}\n")
        return False
        
    except PipelineConnectionError as e:
        print(f"\n🌐 Connection Error:\n{e}\n")
        return False
        
    except PipelineExecutionError as e:
        print(f"\n⚙️  Execution Error:\n{e}\n")
        return False
        
    except Exception as e:
        print(f"\n💥 Unexpected Error: {e}\n")
        return False


if __name__ == "__main__":
    success = main_with_error_handling()
    sys.exit(0 if success else 1)
