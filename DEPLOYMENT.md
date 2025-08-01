# Deployment Guide for EPO URL Downloader

## Prerequisites

1. DigitalOcean Account
2. GitHub Account
3. Git installed locally

## Step-by-Step Deployment

### 1. Prepare Repository

```bash
# Navigate to your project folder
cd "/Users/level3/Desktop/untitled folder/epo_git"

# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit files
git commit -m "Initial commit: EPO URL Downloader"

# Create GitHub repository and push
# (Replace 'yourusername' with your actual GitHub username)
git remote add origin https://github.com/yourusername/epo_git.git
git branch -M main
git push -u origin main
```

### 2. Deploy to DigitalOcean

1. Go to https://cloud.digitalocean.com/apps
2. Click **Create App**
3. Choose **GitHub** as source
4. Select your repository: `yourusername/epo_git`
5. Choose branch: `main`
6. App Platform will auto-detect Python application
7. Configure settings:
   - **App Name**: `epo-url-downloader`
   - **Region**: Choose closest to you
   - **Plan**: Basic ($5/month)
8. Click **Create Resources**
9. Wait for deployment (5-10 minutes)

### 3. Post-Deployment

1. Access your app at the provided URL
2. Test the interface with a small date range first
3. Monitor logs in DigitalOcean dashboard
4. Download generated files through the web interface

## Configuration Files Included

- `requirements.txt` - Python dependencies
- `Procfile` - DigitalOcean deployment command
- `runtime.txt` - Python version specification
- `.do/app.yaml` - DigitalOcean app configuration
- `setup.sh` - Chrome installation script (if needed)

## Environment Variables

The app automatically configures:
- `PORT`: Server port (8080)
- `PYTHONUNBUFFERED`: Logging configuration

## Troubleshooting

### Common Issues:

1. **Chrome Driver Issues**: The app uses webdriver-manager for automatic setup
2. **Memory Issues**: Large date ranges may timeout - use smaller ranges
3. **File Storage**: Files are stored in `/tmp/` and may be cleared on restart

### Monitoring:

- Check app logs in DigitalOcean dashboard
- Monitor resource usage
- Test with small date ranges first

## Cost Estimation

- Basic App: $5/month
- Additional costs for data transfer (minimal for this use case)
- Total estimated cost: ~$5-10/month

## Support

- DigitalOcean Documentation: https://docs.digitalocean.com/products/app-platform/
- App Platform Pricing: https://www.digitalocean.com/pricing/app-platform
