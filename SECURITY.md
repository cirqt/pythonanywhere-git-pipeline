# Security Guide: GitHub Secrets Integration

## **Setting Up GitHub Secrets (Recommended)**

### **Step 1: Get Your PythonAnywhere Credentials**

1. **Username**: Your PythonAnywhere username
2. **API Token**: 
   - Go to https://www.pythonanywhere.com/user/yourusername/account/#api_token
   - Generate a new token if needed
3. **Host**: Your domain (e.g., `yourusername.pythonanywhere.com`)

### **Step 2: Add Secrets to GitHub Repository**

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `PAW_USERNAME` | `your_username` | PythonAnywhere username |
| `PAW_TOKEN` | `your_api_token_here` | PythonAnywhere API token |
| `PAW_HOST` | `yourusername.pythonanywhere.com` | Your PythonAnywhere domain |
| `PAW_PROJECT_PATH` | `/home/yourusername/myproject` | Project path on PythonAnywhere |

### **Step 3: Use in GitHub Actions**

The workflow will automatically use these secrets:

```yaml
- name: Deploy to PythonAnywhere
  env:
    PAW_USERNAME: ${{ secrets.PAW_USERNAME }}
    PAW_TOKEN: ${{ secrets.PAW_TOKEN }}
    PAW_HOST: ${{ secrets.PAW_HOST }}
  run: |
    python github_deploy.py --project-path "${{ secrets.PAW_PROJECT_PATH }}" --branch main
```

## **Usage Methods**

### **Method 1: GitHub Actions (Automatic)**

Once secrets are configured, deployments happen automatically:
- Push to `main` branch triggers deployment
- Manual deployment via GitHub Actions tab

### **Method 2: Local Development with Environment Variables**

```bash
# Set environment variables (Windows)
set PAW_USERNAME=your_username
set PAW_TOKEN=your_token
set PAW_HOST=yourusername.pythonanywhere.com

# Run deployment
python github_deploy.py --project-path "/home/yourusername/project"
```

```bash
# Set environment variables (Linux/Mac)
export PAW_USERNAME=your_username
export PAW_TOKEN=your_token
export PAW_HOST=yourusername.pythonanywhere.com

# Run deployment  
python github_deploy.py --project-path "/home/yourusername/project"
```

### **Method 3: Python Code with Environment Variables**

```python
from main import load_credentials_from_env, PythonAnywhereGitPipeline

# Load from environment variables (GitHub Secrets)
credentials = load_credentials_from_env()
pipeline = PythonAnywhereGitPipeline(credentials)

# Deploy
result = pipeline.execute_git_pull("/home/user/project")
```

### **Method 4: Fallback to YAML (Local Development)**

```python
from main import load_credentials

# Try environment first, fallback to YAML
credentials = load_credentials()  # Auto-detects best method
pipeline = PythonAnywhereGitPipeline(credentials)
```

## **Security Best Practices**

### **DO:**
- Use GitHub Secrets for production deployments
- Use environment variables for local development
- Rotate API tokens regularly
- Use different tokens for different projects if possible
- Keep `config.yaml` in `.gitignore`

### **DON'T:**
- Commit `config.yaml` with real credentials to version control
- Share API tokens in plain text
- Use production tokens for testing
- Store credentials in public repositories

## **Integration Examples**

### **In Your Own Project**

1. **Add as Git Submodule:**
```bash
git submodule add https://github.com/yourusername/pythonanywhere-git-pipeline.git paw_pipeline
```

2. **Add GitHub Secrets:**
- Follow Step 2 above

3. **Create Deployment Workflow:**
```yaml
# .github/workflows/deploy.yml
name: Deploy to PythonAnywhere

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      with:
        submodules: true
    
    - uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r paw_pipeline/requirements.txt
    
    - name: Deploy
      env:
        PAW_USERNAME: ${{ secrets.PAW_USERNAME }}
        PAW_TOKEN: ${{ secrets.PAW_TOKEN }}
        PAW_HOST: ${{ secrets.PAW_HOST }}
      run: |
        python paw_pipeline/github_deploy.py --project-path "${{ secrets.PAW_PROJECT_PATH }}"
```

### **Multiple Projects Deployment**

```python
# deploy_multiple.py
import os
from main import load_credentials_from_env, PythonAnywhereGitPipeline

credentials = load_credentials_from_env()
pipeline = PythonAnywhereGitPipeline(credentials)

projects = [
    {"path": "/home/user/frontend", "branch": "main"},
    {"path": "/home/user/backend", "branch": "main"},
    {"path": "/home/user/api", "branch": "develop"}
]

for project in projects:
    result = pipeline.execute_git_pull(project["path"], project["branch"])
    print(f"{project['path']}: {'Success' if result['success'] else 'Failed'}")
```

## **Troubleshooting**

### **Common Issues:**

1. **Missing Secrets Error:**
   - Ensure all required secrets are added to GitHub
   - Check secret names match exactly (case-sensitive)

2. **API Token Issues:**
   - Verify token is valid and not expired
   - Check token has necessary permissions
   - Try regenerating the token

3. **Connection Failures:**
   - Verify host format (include full domain)
   - Check PythonAnywhere service status
   - Ensure account has console access

4. **Path Issues:**
   - Use absolute paths starting with `/home/username/`
   - Ensure project directory exists on PythonAnywhere
   - Check permissions for the project directory

## **Advanced Configuration**

### **Organization Secrets**

For organizations managing multiple repositories:
1. Go to Organization Settings → Secrets
2. Add organization-level secrets
3. Grant access to specific repositories

### **Environment-Specific Deployments**

```yaml
# Different secrets for different environments
- name: Deploy to Staging
  if: github.ref == 'refs/heads/develop'
  env:
    PAW_USERNAME: ${{ secrets.PAW_STAGING_USERNAME }}
    PAW_TOKEN: ${{ secrets.PAW_STAGING_TOKEN }}
    PAW_HOST: ${{ secrets.PAW_STAGING_HOST }}

- name: Deploy to Production  
  if: github.ref == 'refs/heads/main'
  env:
    PAW_USERNAME: ${{ secrets.PAW_PROD_USERNAME }}
    PAW_TOKEN: ${{ secrets.PAW_PROD_TOKEN }}
    PAW_HOST: ${{ secrets.PAW_PROD_HOST }}
```

This approach ensures your credentials are never exposed in code while maintaining the flexibility of the original YAML-based system for local development.
