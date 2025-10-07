# PythonAnywhere Git Pipeline

Automates git operations on PythonAnywhere through their console API. Uses YAML config or GitHub Secrets.

## Features

- Execute git pull/push/clone on PythonAnywhere remotely
- YAML config or GitHub Secrets for credentials  
- API token authentication
- Basic logging
- Works with other projects

## Installation

Clone and install:
```bash
git clone https://github.com/cirqt/pythonanywhere-git-pipeline.git
cd pythonanywhere-git-pipeline
pip install -r requirements.txt
```

Or install as package:
```bash
pip install -e .
```

## Configuration

### Method 1: GitHub Secrets (for CI/CD) - Recommended

Add these secrets to your repo:
- `PAW_USERNAME` - Your PythonAnywhere username
- `PAW_TOKEN` - Your API token  
- `PAW_HOST` - Your domain (username.pythonanywhere.com)
- `PAW_PROJECT_PATH` - Project path (/home/username/project)
- `PAW_CLI` - **Required** Console ID of an always-open console

#### Setting Up PAW_CLI (Required for Reliable Deployments)

The PAW_CLI approach bypasses PythonAnywhere's browser activation requirement and is **much more reliable** than the traditional console creation method.

**Quick Setup:**
1. **Find your console ID**:
   ```bash
   python test_deployment.py consoles
   ```

2. **Open and keep a console active**:
   - Go to your PythonAnywhere dashboard
   - Click "Consoles" → "Bash" to open a console
   - Keep this browser tab open (or pin it)

3. **Set PAW_CLI environment variable**:
   ```bash
   export PAW_CLI=12345  # Replace with your console ID
   ```
   
4. **Add to GitHub Secrets**:
   - Go to your repo → Settings → Secrets and Variables → Actions
   - Add new secret: `PAW_CLI` with your console ID as the value

5. **Deploy reliably**:
   - All deployments will now use your open console
   - No browser activation needed
   - Much faster and more stable

**Why PAW_CLI is better:**
- ✅ No browser activation delays
- ✅ Faster deployments (no console creation time)
- ✅ More reliable (uses stable, initialized console)  
- ✅ Perfect for CI/CD automation
- ✅ One-time setup, works forever

### Method 2: YAML Config (for local use)

Copy example config:
```bash
cp config.yaml.example config.yaml
```

Edit with your credentials:
```yaml
pythonanywhere:
  username: "your_username"
  token: "your_api_token"
  host: "your_domain.pythonanywhere.com"

projects:
  my_project:
    path: "/home/username/project"
    repository: "https://github.com/user/repo.git"
    branch: "main"
```

Get API token from PythonAnywhere Account → API Token.

Don't commit real credentials to git.

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
    print("Connected to PythonAnywhere")
    result = pipeline.execute_git_pull("/home/yourusername/myproject", "main")
    print("Deployment successful!" if result['success'] else "Deployment failed!")
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
    print("Connected to PythonAnywhere")
    
    # Execute git pull
    result = pipeline.execute_git_pull("/home/yourusername/myproject", "main")
    
    if result['success']:
        print("Git pull completed successfully")
        for cmd_result in result['results']:
            print(f"Output: {cmd_result['output']}")
    else:
        print("Git pull failed")
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    # Execute git push with custom commit message
    push_result = pipeline.execute_git_push("/home/yourusername/myproject", "main", "Updated from PythonAnywhere")
    
    if push_result['success']:
        print("Git push completed successfully")
    else:
        print("Git push failed")
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
git submodule add https://github.com/cirqt/pythonanywhere-git-pipeline.git paw_pipeline
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

## Test Deployment

Use the test script to verify your setup:

```bash
python test_deployment.py
```
#   T e s t   d e p l o y m e n t :   1 
 
 