#!/usr/bin/env python3
"""
Example usage of PythonAnywhere Git Pipeline
"""

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
            print("❌ Failed to connect to PythonAnywhere API")
            return False
        
        print("✅ Connected to PythonAnywhere API")
        
        # Execute git pull
        project_path = "/home/yourusername/myproject"  # Change this to your project path
        branch = "main"  # Change this to your desired branch
        
        print(f"Executing git pull on {project_path} (branch: {branch})...")
        result = pipeline.execute_git_pull(project_path, branch)
        
        # Display results
        if result['success']:
            print("✅ Git pull completed successfully!")
            for cmd_result in result['results']:
                print(f"Command: {cmd_result['command']}")
                print(f"Output: {cmd_result['output']}")
        else:
            print("❌ Git pull failed!")
            if 'error' in result:
                print(f"Error: {result['error']}")
            
        return result['success']
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def example_git_clone():
    """Example: Clone a new repository"""
    try:
        # Load credentials from YAML
        credentials = load_credentials_from_yaml('config.yaml')
        
        # Initialize pipeline
        pipeline = PythonAnywhereGitPipeline(credentials)
        
        # Test connection
        print("Testing connection to PythonAnywhere...")
        if not pipeline.test_connection():
            print("❌ Failed to connect to PythonAnywhere API")
            return False
        
        print("✅ Connected to PythonAnywhere API")
        
        # Clone repository
        repo_url = "https://github.com/yourusername/yourproject.git"  # Change this
        target_path = "/home/yourusername/newproject"  # Change this
        branch = "main"
        
        print(f"Cloning {repo_url} to {target_path} (branch: {branch})...")
        result = pipeline.execute_git_clone(repo_url, target_path, branch)
        
        # Display results
        if result['success']:
            print("✅ Git clone completed successfully!")
            for cmd_result in result['results']:
                print(f"Command: {cmd_result['command']}")
                print(f"Output: {cmd_result['output']}")
        else:
            print("❌ Git clone failed!")
            if 'error' in result:
                print(f"Error: {result['error']}")
            
        return result['success']
        
    except Exception as e:
        print(f"❌ Error: {e}")
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
            print("❌ Failed to connect to PythonAnywhere API")
            return False
        
        print("✅ Connected to PythonAnywhere API")
        
        # Execute git push
        project_path = "/home/yourusername/myproject"  # Change this to your project path
        branch = "main"  # Change this to your desired branch
        commit_message = "Updated project files from PythonAnywhere"  # Custom commit message
        
        print(f"Executing git push on {project_path} (branch: {branch})...")
        result = pipeline.execute_git_push(project_path, branch, commit_message)
        
        # Display results
        if result['success']:
            print("✅ Git push completed successfully!")
            for cmd_result in result['results']:
                print(f"Command: {cmd_result['command']}")
                print(f"Output: {cmd_result['output']}")
        else:
            print("❌ Git push failed!")
            if 'error' in result:
                print(f"Error: {result['error']}")
            
        return result['success']
        
    except Exception as e:
        print(f"❌ Error: {e}")
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
            print("❌ Failed to connect to PythonAnywhere API")
            return False
        
        print("✅ Connected to PythonAnywhere API")
        
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
                print(f"✅ {project['name']} updated successfully")
            else:
                print(f"❌ {project['name']} update failed")
                all_successful = False
        
        return all_successful
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("PythonAnywhere Git Pipeline - Examples\n")
    
    # Example 1: Git pull
    print("=== Example 1: Git Pull ===")
    example_git_pull()
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Git clone
    print("=== Example 2: Git Clone ===")
    example_git_clone()
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Git push
    print("=== Example 3: Git Push ===")
    example_git_push()
    
    print("\n" + "="*50 + "\n")
    
    # Example 4: Multiple operations
    print("=== Example 4: Multiple Operations ===")
    example_multiple_operations()
