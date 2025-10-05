#!/usr/bin/env python3
"""
Professional Deployment Testing

More conventional ways to test your PythonAnywhere Git Pipeline
"""

import json
import datetime
import os
import subprocess
from pathlib import Path


class DeploymentTester:
    """Professional deployment testing class"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.deployment_info_file = Path(project_path) / "deployment_info.json"
    
    def test_console_listing(self):
        """Test console listing functionality for PAW_CLI setup"""
        print("Testing console listing functionality...")
        
        try:
            from main import PythonAnywhereGitPipeline, load_credentials_from_environment
            
            # Load credentials
            try:
                credentials = load_credentials_from_environment()
            except Exception as e:
                print(f"Failed to load credentials: {e}")
                print("Make sure PAW_USERNAME, PAW_TOKEN, and PAW_HOST are set")
                return False
            
            # Initialize pipeline
            pipeline = PythonAnywhereGitPipeline(credentials)
            
            # Test connection
            if not pipeline.test_connection():
                print("Failed to connect to PythonAnywhere API")
                return False
            
            print("Connected to PythonAnywhere API successfully")
            
            # List available consoles
            result = pipeline.list_available_consoles()
            
            if result['success']:
                console_count = result['count']
                print(f"Found {console_count} console sessions:")
                
                if console_count > 0:
                    for console in result['consoles']:
                        console_id = console.get('id')
                        executable = console.get('executable', 'Unknown')
                        print(f"  Console ID: {console_id} (executable: {executable})")
                    
                    # Check if PAW_CLI is already set
                    existing_console = os.getenv('PAW_CLI')
                    if existing_console:
                        print(f"\nPAW_CLI is set to: {existing_console}")
                        if any(str(c.get('id')) == existing_console for c in result['consoles']):
                            print("PAW_CLI console ID is valid!")
                        else:
                            print("Warning: PAW_CLI console ID not found in available consoles")
                    else:
                        print(f"\nTo use always-open console feature:")
                        print(f"1. Open PythonAnywhere dashboard and activate a console")
                        print(f"2. Set: export PAW_CLI={result['consoles'][0].get('id')}")
                        print(f"3. Your deployments will use the open console!")
                else:
                    print("No console sessions found.")
                    print("Create a console in PythonAnywhere dashboard first.")
                
                return True
            else:
                print("Failed to list console sessions!")
                if 'error' in result:
                    print(f"Error: {result['error']}")
                return False
                
        except Exception as e:
            print(f"Console listing test failed: {e}")
            return False

    def create_deployment_marker(self):
        """Create a deployment marker file with metadata"""
        deployment_info = {
            "deployment_id": datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),
            "timestamp": datetime.datetime.now().isoformat(),
            "git_commit": self.get_git_commit_hash(),
            "git_branch": self.get_git_branch(),
            "deployer": "PythonAnywhere Git Pipeline",
            "test_status": "pending"
        }
        
        with open(self.deployment_info_file, 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        print(f"Created deployment marker: {deployment_info['deployment_id']}")
        return deployment_info
    
    def verify_deployment(self):
        """Verify deployment by checking the marker file"""
        if not self.deployment_info_file.exists():
            print("Deployment marker file not found")
            return False
        
        with open(self.deployment_info_file, 'r') as f:
            info = json.load(f)
        
        print("Deployment Verification")
        print("=" * 50)
        print(f"Deployment ID: {info['deployment_id']}")
        print(f"Timestamp: {info['timestamp']}")
        print(f"Git Commit: {info['git_commit']}")
        print(f"Git Branch: {info['git_branch']}")
        print(f"Deployer: {info['deployer']}")
        print("=" * 50)
        
        # Update test status
        info['test_status'] = 'verified'
        info['verified_at'] = datetime.datetime.now().isoformat()
        
        with open(self.deployment_info_file, 'w') as f:
            json.dump(info, f, indent=2)
        
        print("Deployment verified successfully!")
        return True
    
    def get_git_commit_hash(self):
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'], 
                capture_output=True, 
                text=True, 
                cwd=self.project_path
            )
            return result.stdout.strip()[:8]  # Short hash
        except:
            return "unknown"
    
    def get_git_branch(self):
        """Get current git branch"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'], 
                capture_output=True, 
                text=True, 
                cwd=self.project_path
            )
            return result.stdout.strip()
        except:
            return "unknown"
    
    def run_health_check(self):
        """Run a health check to verify deployment"""
        checks = {
            "files_present": self.check_files_present(),
            "git_status": self.check_git_status(),
            "dependencies": self.check_dependencies(),
            "marker_file": self.deployment_info_file.exists()
        }
        
        all_passed = all(checks.values())
        
        print("Health Check Results")
        print("=" * 50)
        for check, status in checks.items():
            status_icon = "PASS" if status else "FAIL"
            print(f"{status_icon} {check.replace('_', ' ').title()}: {'PASS' if status else 'FAIL'}")
        print("=" * 50)
        print(f"Overall Status: {'HEALTHY' if all_passed else 'UNHEALTHY'}")
        
        return all_passed
    
    def check_files_present(self):
        """Check if key files are present"""
        key_files = ['main.py', 'requirements.txt', 'README.md']
        return all((Path(self.project_path) / file).exists() for file in key_files)
    
    def check_git_status(self):
        """Check git status"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'], 
                capture_output=True, 
                text=True, 
                cwd=self.project_path
            )
            # No output means clean working directory
            return len(result.stdout.strip()) == 0
        except:
            return False
    
    def check_dependencies(self):
        """Check if requirements.txt exists"""
        return (Path(self.project_path) / 'requirements.txt').exists()


def create_version_file():
    """Create a version file - more professional approach"""
    version_info = {
        "version": "1.0.0",
        "build_number": int(datetime.datetime.now().timestamp()),
        "build_date": datetime.datetime.now().isoformat(),
        "git_commit": get_git_commit(),
        "environment": "production"
    }
    
    with open("version.json", "w") as f:
        json.dump(version_info, f, indent=2)
    
    print(f"Created version file: {version_info['version']}")
    return version_info


def get_git_commit():
    """Get git commit hash"""
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True)
        return result.stdout.strip()[:8]
    except:
        return "unknown"


def simple_deployment_test():
    """Simple deployment test - your original idea but cleaner"""
    test_file = "DEPLOYMENT_TEST.md"
    
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Extract current counter
        import re
        match = re.search(r'Test #(\d+)', content)
        counter = int(match.group(1)) + 1 if match else 1
    else:
        counter = 1
    
    # Create/update test file
    test_content = f"""# Deployment Test
    
Test #{counter}
Deployed at: {datetime.datetime.now().isoformat()}
Git commit: {get_git_commit()}

This file verifies that the deployment pipeline is working correctly.
"""
    
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print(f"Updated deployment test file - Test #{counter}")
    return counter


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        project_path = sys.argv[2] if len(sys.argv) > 2 else "."
        
        tester = DeploymentTester(project_path)
        
        if command == "create":
            tester.create_deployment_marker()
        elif command == "verify":
            tester.verify_deployment()
        elif command == "health":
            tester.run_health_check()
        elif command == "simple":
            simple_deployment_test()
        elif command == "version":
            create_version_file()
        elif command == "consoles":
            tester.test_console_listing()
        else:
            print("Usage: python test_deployment.py [create|verify|health|simple|version|consoles] [project_path]")
    else:
        print("Professional Deployment Testing Tools")
        print("Usage: python test_deployment.py [create|verify|health|simple|version] [project_path]")
