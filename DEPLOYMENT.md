# Deployment Guide

This guide provides instructions for deploying the Premier League Player Role Discovery app to Streamlit Community Cloud.

## Prerequisites

- GitHub account
- Streamlit Community Cloud account (free)
- Git installed on your local machine

## Local Testing

Before deploying, make sure the app runs correctly on your local machine:

```bash
# Activate your environment
conda activate prem-discovery

# Install dependencies
pip install -r requirements.txt

# Run validation tests
python run_app.py --test-only

# Run the app locally
python run_app.py
```

Visit `http://localhost:8501` in your browser to verify the app works correctly.

## Deployment Steps

### 1. Create a GitHub Repository

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit"

# Create a new repository on GitHub and push
git remote add origin https://github.com/yourusername/premier-league-role-discovery.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Streamlit Community Cloud

1. Go to [Streamlit Community Cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository, branch (main), and the main file path (`app/Home.py`)
5. Click "Deploy"

Your app will be deployed and accessible at `https://yourusername-premier-league-role-discovery.streamlit.app`

## Configuration

### Environment Variables

If needed, you can set environment variables in the Streamlit Cloud dashboard:

1. Go to your app settings
2. Click on "Secrets"
3. Add any required environment variables in TOML format:

```toml
[env]
LOG_LEVEL = "INFO"
```

### Advanced Settings

Additional settings can be configured in the Streamlit Cloud dashboard:

- **Memory:** Adjust if the app needs more resources
- **Python Version:** Ensure it matches your local environment
- **Custom Domains:** Set up a custom domain if desired

## Troubleshooting

If you encounter issues during deployment:

1. Check the app logs in the Streamlit Cloud dashboard
2. Verify all dependencies are correctly listed in `requirements.txt`
3. Ensure all file paths use relative paths from the app directory
4. Check that all required data files are included in the repository

## Maintenance

To update the deployed app:

1. Make changes locally and test
2. Commit and push to GitHub
3. Streamlit Cloud will automatically redeploy your app

## Resources

- [Streamlit Deployment Documentation](https://docs.streamlit.io/streamlit-cloud)
- [GitHub Documentation](https://docs.github.com/en)
- [Conda Environment Management](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
