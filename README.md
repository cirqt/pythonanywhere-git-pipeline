# PythonAnywhere Git Pipeline

Automates git operations on PythonAnywhere through their console API. Two usage methods available.

## Two Main Usage Methods

### 1. GitHub Actions Pipeline (Recommended)
Use this for automatic deployment when you push to your repository. Copy the workflow file to your repo and set up GitHub secrets.

### 2. Standalone Python Script
Use this if you prefer to manually run deployments or integrate into your own workflow without GitHub Actions.

## Method 1: GitHub Actions Pipeline

Copy `.github/workflows/external-usage-example.yml` to your repository and set these GitHub Secrets:
- `PAW_USERNAME` - Your PythonAnywhere username
- `PAW_TOKEN` - Your API token  
- `PAW_HOST` - Your domain (username.pythonanywhere.com)
- `PAW_PROJECT_PATH` - Project path (/home/username/project)
- `PAW_CLI` - Console ID of a pre-initialized console

## Method 2: Standalone Script

Download `individualPullToPAW.py` and run it directly:
```bash
curl -O https://raw.githubusercontent.com/cirqt/pythonanywhere-git-pipeline/main/individualPullToPAW.py
python individualPullToPAW.py
```
## Setup Instructions

### For GitHub Actions (Method 1):
1. Copy `.github/workflows/external-usage-example.yml` to your repository
2. Set up GitHub Secrets in your repo (Settings → Secrets and Variables → Actions):

**Required Secrets:**
   - `PAW_USERNAME` - Your PythonAnywhere username
   - `PAW_TOKEN` - Your API token from PythonAnywhere Account → API Token
   - `PAW_HOST` - Your domain (username.pythonanywhere.com) 
   - `PAW_PROJECT_PATH` - Project path (/home/username/project)
   - `PAW_CLI` - Console ID of a pre-initialized console

**For Private Repositories (Optional):**
   - `GIT_USERNAME` - Your GitHub username
   - `GIT_TOKEN` - Your GitHub Personal Access Token

### For Standalone Script (Method 2):
1. Download the script:
   ```bash
   curl -O https://raw.githubusercontent.com/cirqt/pythonanywhere-git-pipeline/main/individualPullToPAW.py
   ```
2. Set environment variables:
   ```bash
   export PAW_USERNAME="your_username"
   export PAW_TOKEN="your_token" 
   export PAW_HOST="username.pythonanywhere.com"
   export PAW_PROJECT_PATH="/home/username/project"
   export PAW_CLI="console_id"
   
   # For private repositories (optional):
   export GIT_USERNAME="your_github_username"
   export GIT_TOKEN="your_github_token"
   export PAW_CLI="console_id"
   ```
3. Run the script:
   ```bash
   python individualPullToPAW.py
   ```

### Finding Your Console ID:
1. Open a console in PythonAnywhere dashboard and keep it open
2. Find your console ID in the browser URL: `https://www.pythonanywhere.com/user/username/consoles/12345678/`
3. Use `12345678` as your `PAW_CLI` value

The PAW_CLI approach bypasses PythonAnywhere's browser activation requirement and is much more reliable.

## Files in This Repository

- `main.py` - Core pipeline code (used by GitHub Actions)
- `github_deploy.py` - Deployment logic (used by GitHub Actions)  
- `individualPullToPAW.py` - Standalone script for manual use
- `requirements.txt` - Python dependencies
- `.github/workflows/external-usage-example.yml` - Example workflow file

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify your API token is correct and active
   - Get a new token from PythonAnywhere Account → API Token

2. **Console ID Issues**
   - Ensure you have an open console in PythonAnywhere dashboard
   - Copy the console ID from the browser URL

3. **Git Command Failed**
   - Ensure the repository exists and you have access
   - Check if the project path is correct
   - Verify Git is configured properly on PythonAnywhere

### Security Notes

- Never commit credentials to version control
- Use GitHub Secrets for environment variables
- Regularly rotate your API tokens

## Support

For issues, check the console output for detailed error messages and ensure your PythonAnywhere account has console access.
