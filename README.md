# PythonAnywhere Git Pipeline

Automates git operations on PythonAnywhere through their console API. Uses YAML config or GitHub Secrets.

## Features

- Execute git pull on PythonAnywhere remotely
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
## Configuration

Add these secrets to your repo:
- `PAW_USERNAME` - Your PythonAnywhere username
- `PAW_TOKEN` - Your API token  
- `PAW_HOST` - Your domain (username.pythonanywhere.com)
- `PAW_PROJECT_PATH` - Project path (/home/username/project)
- `PAW_CLI` - Console ID of a pre-initialized console

The PAW_CLI approach bypasses PythonAnywhere's browser activation requirement

**Quick Setup:**
You can find your console ID in the web browser link when you enter the console
```https://www.pythonanywhere.com/user/username/consoles/12345678/```
12345678 - console ID
   
4. **Add to GitHub Secrets**:
   - Go to your repo → Settings → Secrets and Variables → Actions
   - Add new secret: `PAW_CLI` with your console ID as the value

Get API token from PythonAnywhere Account → API Token.

Don't commit real credentials to git.

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


### Support

- Check PythonAnywhere's API documentation
- Review the console output for detailed error messages
- Ensure your PythonAnywhere account is active and has console access

### .yml exmaple
```
# Simple GitHub Actions workflow for PythonAnywhere deployment
# Copy this to your repository at: .github/workflows/deploy.yml
#
# Required GitHub Secrets:
# - PAW_USERNAME: Your PythonAnywhere username
# - PAW_TOKEN: Your API token from PythonAnywhere Account → API Token
# - PAW_HOST: Your domain (e.g., yourusername.pythonanywhere.com)
# - PAW_CLI: Console ID from open console (get from URL: /consoles/12345/)
# - PAW_PROJECT_PATH: Project path (e.g., /home/yourusername/myproject)

name: Deploy to PythonAnywhere

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: pip install requests pyyaml
    
    - name: Deploy
      env:
        PAW_USERNAME: ${{ secrets.PAW_USERNAME }}
        PAW_TOKEN: ${{ secrets.PAW_TOKEN }}
        PAW_HOST: ${{ secrets.PAW_HOST }}
        PAW_CLI: ${{ secrets.PAW_CLI }}
        PAW_PROJECT_PATH: ${{ secrets.PAW_PROJECT_PATH }}
      run: python github_deploy.py --project-path "$PAW_PROJECT_PATH" --branch main

```
