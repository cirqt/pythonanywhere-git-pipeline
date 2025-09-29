# PythonAnywhere Git Pipeline

A Python package for executing Git operations on PythonAnywhere hosting service via their console API using credentials provided through YAML configuration files.

## Features

- 🚀 Execute `git pull` commands on PythonAnywhere remotely
- � Execute `git push` commands with automatic commit
- �📁 Clone repositories to PythonAnywhere
- 🔧 YAML-based configuration management
- 🛡️ Secure API token authentication
- 📝 Comprehensive logging
- 🔌 Easy integration with other projects

## Installation

### Install from Source

```bash
git clone https://github.com/yourusername/PAWgithubPipeline.git
cd PAWgithubPipeline
pip install -r requirements.txt
```

### Install as Package

```bash
pip install -e .
```

## Configuration

### 🔒 **Method 1: GitHub Secrets (Recommended for Production)**

For secure deployments, use GitHub Secrets instead of YAML files:

1. **Add secrets to your GitHub repository:**
   - Go to Settings → Secrets and variables → Actions
   - Add these secrets:
     - `PAW_USERNAME`: Your PythonAnywhere username
     - `PAW_TOKEN`: Your PythonAnywhere API token
     - `PAW_HOST`: Your domain (e.g., `yourusername.pythonanywhere.com`)
     - `PAW_PROJECT_PATH`: Project path (e.g., `/home/yourusername/myproject`)

2. **The GitHub Actions workflow will automatically use these secrets**

### 📄 **Method 2: YAML Configuration (Local Development)**

1. Copy the example configuration file:
```bash
cp config.yaml.example config.yaml
```

2. Edit `config.yaml` with your PythonAnywhere credentials:

```yaml
pythonanywhere:
  username: "your_username"
  token: "your_api_token"
  host: "your_domain.pythonanywhere.com"

projects:
  my_project:
    path: "/home/yourusername/myproject"
    repository: "https://github.com/yourusername/myproject.git"
    branch: "main"
```

### Getting Your API Token

1. Log into your PythonAnywhere account
2. Go to Account → API Token
3. Generate a new token if you don't have one
4. Add the token to GitHub Secrets or your `config.yaml`

> **⚠️ Security Note:** Never commit `config.yaml` with real credentials to version control. Use GitHub Secrets for production deployments.

## Usage

### Command Line Interface

#### Basic Git Pull
```bash
python main.py --config config.yaml --project-path "/home/yourusername/myproject" --operation pull
```

#### Git Pull with Specific Branch
```bash
python main.py --config config.yaml --project-path "/home/yourusername/myproject" --branch develop --operation pull
```

#### Clone Repository
```bash
python main.py --config config.yaml --project-path "/home/yourusername/newproject" --repo-url "https://github.com/user/repo.git" --operation clone
```

#### Git Push with Commit
```bash
python main.py --config config.yaml --project-path "/home/yourusername/myproject" --operation push --commit-message "Updated project files"
```

### Python API

#### Using GitHub Secrets (Recommended)
```python
from main import PythonAnywhereGitPipeline, load_credentials_from_env

# Load credentials from environment variables (GitHub Secrets)
credentials = load_credentials_from_env()

# Initialize pipeline
pipeline = PythonAnywhereGitPipeline(credentials)

# Test connection and deploy
if pipeline.test_connection():
    print("✅ Connected to PythonAnywhere")
    result = pipeline.execute_git_pull("/home/yourusername/myproject", "main")
    print("✅ Deployment successful!" if result['success'] else "❌ Deployment failed!")
```

#### Using YAML Configuration
```python
from main import PythonAnywhereGitPipeline, load_credentials_from_yaml

# Load credentials from YAML
credentials = load_credentials_from_yaml('config.yaml')

# Initialize pipeline
pipeline = PythonAnywhereGitPipeline(credentials)

# Test connection
if pipeline.test_connection():
    print("✅ Connected to PythonAnywhere")
    
    # Execute git pull
    result = pipeline.execute_git_pull("/home/yourusername/myproject", "main")
    
    if result['success']:
        print("✅ Git pull completed successfully")
        for cmd_result in result['results']:
            print(f"Output: {cmd_result['output']}")
    else:
        print("❌ Git pull failed")
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    # Execute git push with custom commit message
    push_result = pipeline.execute_git_push("/home/yourusername/myproject", "main", "Updated from PythonAnywhere")
    
    if push_result['success']:
        print("✅ Git push completed successfully")
    else:
        print("❌ Git push failed")
```

#### Smart Credential Loading (Auto-detect)
```python
from main import PythonAnywhereGitPipeline, load_credentials

# Try environment variables first, fallback to config.yaml
credentials = load_credentials()
pipeline = PythonAnywhereGitPipeline(credentials)
```

### Integration in Other Projects

#### Using as a Git Submodule

1. Add as submodule to your project:
```bash
git submodule add https://github.com/yourusername/PAWgithubPipeline.git paw_pipeline
```

2. Create your project's configuration:
```yaml
# your_project_config.yaml
pythonanywhere:
  username: "your_username"
  token: "your_api_token"
  host: "your_domain.pythonanywhere.com"
```

3. Use in your Python code:
```python
import sys
sys.path.append('paw_pipeline')

from main import PythonAnywhereGitPipeline, load_credentials_from_yaml

credentials = load_credentials_from_yaml('your_project_config.yaml')
pipeline = PythonAnywhereGitPipeline(credentials)

# Deploy your project
result = pipeline.execute_git_pull("/home/yourusername/your_project")
if result['success']:
    print("Deployment successful!")
```

#### Using as an Installed Package

```python
from pythonanywhere_git_pipeline import PythonAnywhereGitPipeline, load_credentials_from_yaml

# Your deployment script
def deploy_to_pythonanywhere(config_path, project_path):
    credentials = load_credentials_from_yaml(config_path)
    pipeline = PythonAnywhereGitPipeline(credentials)
    
    if not pipeline.test_connection():
        raise Exception("Failed to connect to PythonAnywhere")
    
    result = pipeline.execute_git_pull(project_path)
    return result['success']

# Usage
success = deploy_to_pythonanywhere('config.yaml', '/home/yourusername/myapp')
```

## YAML Configuration Reference

### Required Fields

- `pythonanywhere.username`: Your PythonAnywhere username
- `pythonanywhere.token`: Your PythonAnywhere API token
- `pythonanywhere.host`: Your PythonAnywhere domain

### Optional Project Configuration

```yaml
projects:
  project_name:
    path: "/home/username/project_path"
    repository: "https://github.com/user/repo.git"
    branch: "main"
```

## API Reference

### Classes

#### `PAWCredentials`
Data class for storing PythonAnywhere credentials.

#### `PythonAnywhereGitPipeline`
Main class for handling Git operations.

**Methods:**
- `test_connection()`: Test API connection
- `execute_git_pull(project_path, branch='main')`: Execute git pull
- `execute_git_clone(repo_url, target_path, branch='main')`: Clone repository
- `execute_git_push(project_path, branch='main', commit_message=None)`: Execute git add, commit, and push

### Functions

#### `load_credentials_from_yaml(yaml_path)`
Load credentials from YAML configuration file.

## Error Handling

The package provides comprehensive error handling:

- Connection failures
- Authentication errors
- Command execution failures
- Console creation/cleanup issues

All errors are logged and returned in the result dictionary.

## Security Notes

- Never commit your `config.yaml` with real credentials to version control
- Use environment variables for sensitive information in production
- Regularly rotate your API tokens
- Keep your configuration files secure

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify your API token is correct
   - Check if your token has expired

2. **Console Creation Failed**
   - Check if you have available console slots
   - Verify your PythonAnywhere plan supports console access

3. **Git Command Failed**
   - Ensure the repository exists and you have access
   - Check if the project path is correct
   - Verify Git is properly configured on PythonAnywhere

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Support

- Check PythonAnywhere's API documentation
- Review the console output for detailed error messages
- Ensure your PythonAnywhere account is active and has console access
