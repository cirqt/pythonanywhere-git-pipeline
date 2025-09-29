#!/usr/bin/env python3
"""
Deployment script example for integrating PythonAnywhere Git Pipeline
into other projects.

This script can be customized and included in your projects to automate
deployment to PythonAnywhere.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the PAW pipeline to Python path if it's a submodule
pipeline_path = Path(__file__).parent / 'paw_pipeline'
if pipeline_path.exists():
    sys.path.insert(0, str(pipeline_path))

try:
    from main import PythonAnywhereGitPipeline, load_credentials_from_yaml
except ImportError:
    print("❌ PythonAnywhere Git Pipeline not found!")
    print("   Make sure you have either:")
    print("   1. Installed the package: pip install pythonanywhere-git-pipeline")
    print("   2. Added it as a git submodule in 'paw_pipeline' directory")
    print("   3. Have the main.py file in the same directory")
    sys.exit(1)


class ProjectDeployer:
    """
    Project-specific deployer that uses PythonAnywhere Git Pipeline
    """
    
    def __init__(self, config_path: str):
        """
        Initialize deployer with configuration
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.credentials = None
        self.pipeline = None
        
    def load_configuration(self):
        """Load configuration and initialize pipeline"""
        try:
            self.credentials = load_credentials_from_yaml(self.config_path)
            self.pipeline = PythonAnywhereGitPipeline(self.credentials)
            return True
        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
            return False
    
    def test_connection(self):
        """Test connection to PythonAnywhere"""
        if not self.pipeline:
            return False
        
        print("🔍 Testing connection to PythonAnywhere...")
        if self.pipeline.test_connection():
            print("✅ Connection successful!")
            return True
        else:
            print("❌ Connection failed!")
            return False
    
    def deploy_project(self, project_path: str, branch: str = "main"):
        """
        Deploy a single project
        
        Args:
            project_path: Path to project on PythonAnywhere
            branch: Git branch to deploy
        """
        print(f"🚀 Deploying project: {project_path}")
        print(f"   Branch: {branch}")
        
        result = self.pipeline.execute_git_pull(project_path, branch)
        
        if result['success']:
            print("✅ Deployment successful!")
            for cmd_result in result['results']:
                if cmd_result['output'].strip():
                    print(f"   Output: {cmd_result['output'].strip()}")
        else:
            print("❌ Deployment failed!")
            if 'error' in result:
                print(f"   Error: {result['error']}")
            for cmd_result in result['results']:
                if cmd_result.get('error'):
                    print(f"   Command Error: {cmd_result['error']}")
        
        return result['success']
    
    def deploy_multiple_projects(self, projects: list):
        """
        Deploy multiple projects
        
        Args:
            projects: List of project dictionaries with 'path' and optional 'branch'
        """
        successful_deployments = 0
        total_projects = len(projects)
        
        print(f"🚀 Deploying {total_projects} projects...")
        
        for i, project in enumerate(projects, 1):
            project_path = project['path']
            branch = project.get('branch', 'main')
            
            print(f"\n[{i}/{total_projects}] Deploying: {project_path}")
            
            if self.deploy_project(project_path, branch):
                successful_deployments += 1
        
        print(f"\n📊 Deployment Summary:")
        print(f"   Successful: {successful_deployments}/{total_projects}")
        print(f"   Failed: {total_projects - successful_deployments}/{total_projects}")
        
        return successful_deployments == total_projects


def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description='Deploy projects to PythonAnywhere')
    parser.add_argument('--config', '-c', required=True, 
                       help='Path to YAML configuration file')
    parser.add_argument('--project-path', '-p', 
                       help='Single project path to deploy')
    parser.add_argument('--branch', '-b', default='main', 
                       help='Git branch to deploy (default: main)')
    parser.add_argument('--multiple', '-m', action='store_true',
                       help='Deploy multiple projects defined in config')
    
    args = parser.parse_args()
    
    # Initialize deployer
    deployer = ProjectDeployer(args.config)
    
    # Load configuration
    if not deployer.load_configuration():
        return 1
    
    # Test connection
    if not deployer.test_connection():
        return 1
    
    # Deploy projects
    if args.multiple:
        # Load project definitions from config
        try:
            import yaml
            with open(args.config, 'r') as f:
                config = yaml.safe_load(f)
            
            projects = []
            if 'projects' in config:
                for name, project_config in config['projects'].items():
                    projects.append({
                        'path': project_config['path'],
                        'branch': project_config.get('branch', 'main')
                    })
            
            if not projects:
                print("❌ No projects defined in configuration file")
                return 1
            
            success = deployer.deploy_multiple_projects(projects)
            
        except Exception as e:
            print(f"❌ Failed to load project configurations: {e}")
            return 1
    
    elif args.project_path:
        # Deploy single project
        success = deployer.deploy_project(args.project_path, args.branch)
    
    else:
        print("❌ Please specify either --project-path or --multiple")
        return 1
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
