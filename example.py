#!/usr/bin/env python3
"""
Example usage of PythonAnywhere Git Pipeline
"""
# Test counter for deployment verification: 22

from main import PythonAnywhereGitPipeline, load_credentials_from_yaml


def example_git_pull():
    """Example: Execute git pull on an existing project"""
    try:
        # Load credentials from YAML
        credentials = load_credentials_from_yaml('config.yaml')
        
        # Initialize pipeline
        pipeline = PythonAnywhereGitPipeline(credentials)
        
        # Test connection
        print("Testing connection to PythonAnywhere...")
        if not pipeline.test_connection():
            print("Failed to connect to PythonAnywhere API")
            return False
        
        print("Connected to PythonAnywhere API")
        
        # Execute git pull
        project_path = "/home/yourusername/myproject"  # Change this to your project path
        branch = "main"  # Change this to your desired branch
        
        print(f"Executing git pull on {project_path} (branch: {branch})...")
        result = pipeline.execute_git_pull(project_path, branch)
        
        # Display results
        if result['success']:
            print("Git pull completed successfully!")
            for cmd_result in result['results']:
                print(f"Command: {cmd_result['command']}")
                print(f"Output: {cmd_result['output']}")
        else:
            print("Git pull failed!")
            if 'error' in result:
                print(f"Error: {result['error']}")
            
        return result['success']
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def example_git_push():
    """Example: Execute git add, commit, and push on a project"""
    try:
        # Load credentials from YAML
        credentials = load_credentials_from_yaml('config.yaml')
        
        # Initialize pipeline
        pipeline = PythonAnywhereGitPipeline(credentials)
        
        # Test connection
        print("Testing connection to PythonAnywhere...")
        if not pipeline.test_connection():
            print("Failed to connect to PythonAnywhere API")
            return False
        
        print("Connected to PythonAnywhere API")
        
        # Execute git push
        project_path = "/home/yourusername/myproject"  # Change this to your project path
        branch = "main"  # Change this to your desired branch
        commit_message = "Updated project files from PythonAnywhere"  # Custom commit message
        
        print(f"Executing git push on {project_path} (branch: {branch})...")
        result = pipeline.execute_git_push(project_path, branch, commit_message)
        
        # Display results
        if result['success']:
            print("Git push completed successfully!")
            for cmd_result in result['results']:
                print(f"Command: {cmd_result['command']}")
                print(f"Output: {cmd_result['output']}")
        else:
            print("Git push failed!")
            if 'error' in result:
                print(f"Error: {result['error']}")
            
        return result['success']
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def example_list_consoles():
    """Example: List available console sessions to find console IDs for PAW_CLI"""
    try:
        # Load credentials from YAML
        credentials = load_credentials_from_yaml('config.yaml')
        
        # Initialize pipeline
        pipeline = PythonAnywhereGitPipeline(credentials)
        
        # Test connection
        print("Testing connection to PythonAnywhere...")
        if not pipeline.test_connection():
            print("Failed to connect to PythonAnywhere API")
            return False
        
        print("Connected to PythonAnywhere API")
        
        # List available consoles
        print("Listing available console sessions...")
        result = pipeline.list_available_consoles()
        
        if result['success']:
            print(f"Found {result['count']} console sessions:")
            for console in result['consoles']:
                console_id = console.get('id')
                executable = console.get('executable', 'Unknown')
                print(f"  Console ID: {console_id} (executable: {executable})")
            
            if result['count'] > 0:
                print("\nTo use an always-open console:")
                print("1. Open PythonAnywhere dashboard in your browser")
                print("2. Click on one of the console sessions to activate it")
                print("3. Set the PAW_CLI environment variable to the console ID")
                print(f"   Example: export PAW_CLI={result['consoles'][0].get('id')}")
                print("4. Run your git operations - they will use the open console!")
            else:
                print("\nNo console sessions found. Create one in PythonAnywhere dashboard first.")
                
        else:
            print("Failed to list console sessions!")
            if 'error' in result:
                print(f"Error: {result['error']}")
            
        return result['success']
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def example_with_existing_console():
    """Example: Use PAW_CLI environment variable with existing console"""
    import os
    
    # Check if PAW_CLI is set
    existing_console = os.getenv('PAW_CLI')
    if not existing_console:
        print("PAW_CLI environment variable not set!")
        print("Please run example_list_consoles() first to find a console ID")
        print("Then set: export PAW_CLI=<console_id>")
        return False
    
    try:
        # Load credentials from YAML
        credentials = load_credentials_from_yaml('config.yaml')
        
        # Initialize pipeline
        pipeline = PythonAnywhereGitPipeline(credentials)
        
        # Test connection
        print("Testing connection to PythonAnywhere...")
        if not pipeline.test_connection():
            print("Failed to connect to PythonAnywhere API")
            return False
        
        print(f"Connected to PythonAnywhere API")
        print(f"Using existing console: {existing_console}")
        
        # Execute git pull using existing console
        project_path = "/home/yourusername/myproject"  # Change this to your project path
        branch = "main"  # Change this to your desired branch
        
        print(f"Executing git pull on {project_path} (branch: {branch}) using existing console...")
        result = pipeline.execute_git_pull(project_path, branch)
        
        # Display results
        if result['success']:
            print("Git pull completed successfully using existing console!")
            print("No console creation or initialization needed!")
            for cmd_result in result['results']:
                print(f"Command: {cmd_result['command']}")
                print(f"Output: {cmd_result['output']}")
        else:
            print("Git pull failed!")
            if 'error' in result:
                print(f"Error: {result['error']}")
            
        return result['success']
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def example_multiple_operations():
    """Example: Execute multiple git operations"""
    try:
        # Load credentials from YAML
        credentials = load_credentials_from_yaml('config.yaml')
        
        # Initialize pipeline
        pipeline = PythonAnywhereGitPipeline(credentials)
        
        # Test connection
        if not pipeline.test_connection():
            print("Failed to connect to PythonAnywhere API")
            return False
        
        print("Connected to PythonAnywhere API")
        
        # Define multiple projects
        projects = [
            {
                'name': 'Project 1',
                'path': '/home/yourusername/project1',
                'branch': 'main'
            },
            {
                'name': 'Project 2', 
                'path': '/home/yourusername/project2',
                'branch': 'develop'
            }
        ]
        
        # Execute git pull for each project
        all_successful = True
        for project in projects:
            print(f"\nUpdating {project['name']}...")
            result = pipeline.execute_git_pull(project['path'], project['branch'])
            
            if result['success']:
                print(f"{project['name']} updated successfully")
            else:
                print(f"{project['name']} update failed")
                all_successful = False
        
        return all_successful
        
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    print("PythonAnywhere Git Pipeline - Simplified Examples\n")
    print("Recommended: Use PAW_CLI for reliable deployments!\n")
    
    # Example 1: Setup PAW_CLI (first-time setup)
    print("=== Setup: Find Console ID for PAW_CLI ===")
    example_list_consoles()
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Recommended approach with PAW_CLI
    print("=== Recommended: Git Pull with PAW_CLI ===")
    example_with_existing_console()
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Git push with PAW_CLI
    print("=== Git Push with PAW_CLI ===")
    import os
    if os.getenv('PAW_CLI'):
        example_git_push()
    else:
        print("PAW_CLI not set - skipping git push example")
        print("Set PAW_CLI first for reliable deployments!")
    
    print("\n" + "="*50 + "\n")
    
    # Example 4: Multiple operations with PAW_CLI
    print("=== Multiple Operations with PAW_CLI ===")
    if os.getenv('PAW_CLI'):
        example_multiple_operations()
    else:
        print("PAW_CLI not set - skipping multiple operations example")
    
    print("\n" + "="*60 + "\n")
    print("Note: Traditional console creation methods are deprecated.")
    print("Use PAW_CLI for faster, more reliable deployments!")
