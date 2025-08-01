# EPO URL Downloader - DigitalOcean Deployment

This application scrapes the European Patent Office (EPO) publication server to extract ZIP file URLs for specified year and week ranges. The extracted URLs are saved to text files in the server's local storage.

## Features

- 🚀 Ultra-fast EPO ZIP URL extraction
- 📅 Configurable year and week ranges
- 💾 Local file storage on DigitalOcean
- 🌐 Web interface for easy operation
- 📁 Download generated URL files

## Getting Started

**Note: Following these steps may result in charges for the use of DigitalOcean services.**

### Requirements

* You need a DigitalOcean account. If you don't already have one, you can sign up at https://cloud.digitalocean.com/registrations/new.

## Deploying the App

### Option 1: Using DigitalOcean App Platform (Recommended)

1. Fork this repository to your GitHub account
2. Go to https://cloud.digitalocean.com/apps
3. Click **Create App**
4. Select **GitHub** as your source
5. Choose your forked repository
6. Select the `main` branch
7. App Platform will automatically detect the Python application
8. Configure your app:
   - **App Name**: epo-url-downloader (or your preferred name)
   - **Region**: Choose the closest region to you
   - **Plan**: Basic plan is sufficient for most use cases
9. Click **Create Resources**
10. Wait for the build to complete (this may take several minutes)
11. Once deployed, click the **Live App** link to access your application

### Option 2: Manual Deployment

If you want to customize the deployment:

1. Fork this repository
2. Update the `.do/app.yaml` file with your repository details
3. Follow the App Platform deployment process

## Using the Application

1. Access your deployed application URL
2. Set your desired parameters:
   - **Year Start**: Starting year (1979-2025)
   - **Year End**: Ending year (1979-2025)
   - **Week Start**: Starting week (1-52)
   - **Week End**: Ending week (1-52)
3. Click **Start Download**
4. Wait for the process to complete (this may take a while depending on the range)
5. Download the generated text files containing the URLs

## File Storage

- All generated files are stored in `/tmp/epo_patent/` on the server
- Files are named using the format: `{year}_{week}.txt`
- Each file contains one URL per line
- Files can be downloaded through the web interface

## Dependencies

- Python 3.9+
- Selenium WebDriver
- Chrome/Chromium browser
- Flask web framework
- Gunicorn WSGI server

## Environment Variables

- `PORT`: Server port (default: 8080)
- `PYTHONUNBUFFERED`: Set to "1" for proper logging

## Technical Details

The application uses:
- **Selenium WebDriver** with headless Chrome for web scraping
- **Flask** for the web interface
- **Gunicorn** as the WSGI server
- **DigitalOcean App Platform** for hosting

## Limitations

- Processing large date ranges may take considerable time
- Server storage is temporary and files may be cleared on restart
- Chrome WebDriver requires adequate memory allocation

## Making Changes

If you forked the repository:

1. Make your changes to the code
2. Commit and push to your `main` branch
3. App Platform will automatically redeploy your application
4. Monitor the build process in the DigitalOcean dashboard

## Learn More

- [DigitalOcean App Platform Documentation](https://www.digitalocean.com/docs/app-platform/)
- [EPO Publication Server](https://data.epo.org/publication-server/)

## Support

For issues related to:
- **DigitalOcean deployment**: Check the App Platform documentation
- **Application functionality**: Review the code and logs
- **EPO website changes**: The scraping logic may need updates

## Deleting the App

When you no longer need this sample application running live, you can delete it by following these steps:
1. Visit the Apps control panel at https://cloud.digitalocean.com/apps.
2. Navigate to the sample app.
3. In the **Settings** tab, click **Destroy**.

**Note: If you do not delete your app, charges for using DigitalOcean services will continue to accrue.**
