# Security Setup

## Setting Up GitHub Secrets

### Get Your Credentials

1. Username: Your PythonAnywhere username
2. API Token: Go to pythonanywhere.com/user/username/account/#api_token
3. Host: Your domain (username.pythonanywhere.com)

### Add to GitHub

1. Go to repo Settings → Secrets and variables → Actions
2. Click New repository secret
3. Add these:

- `PAW_USERNAME` - your username
- `PAW_TOKEN` - your api token  
- `PAW_HOST` - your domain
- `PAW_PROJECT_PATH` - project path like /home/user/project

### Usage

GitHub Actions uses these automatically. For local development:

```bash
# Windows
set PAW_USERNAME=your_username
set PAW_TOKEN=your_token
set PAW_HOST=yourusername.pythonanywhere.com

# Linux/Mac
export PAW_USERNAME=your_username
export PAW_TOKEN=your_token
export PAW_HOST=yourusername.pythonanywhere.com
```

## Security Rules

Do:
- Use GitHub Secrets for production
- Use env vars for local dev
- Rotate tokens regularly
- Keep config.yaml in .gitignore

Don't:
- Commit real credentials to git
- Share tokens in plain text
- Use production tokens for testing

## Integration

Add as submodule:
```bash
git submodule add https://github.com/user/repo.git paw_pipeline
```

Create workflow:
```yaml
name: Deploy
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Deploy
      env:
        PAW_USERNAME: ${{ secrets.PAW_USERNAME }}
        PAW_TOKEN: ${{ secrets.PAW_TOKEN }}
        PAW_HOST: ${{ secrets.PAW_HOST }}
      run: python paw_pipeline/github_deploy.py --project-path "${{ secrets.PAW_PROJECT_PATH }}"
```

## Troubleshooting

Common problems:
- Missing secrets: Check they're added to GitHub
- Token issues: Try regenerating it
- Connection failures: Check host format
- Path issues: Use absolute paths starting with /home/user/
