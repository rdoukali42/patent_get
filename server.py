import os
import time
import requests
import re
import json
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

class FastEPODownloader:
    def __init__(self, year='2025', week='30'):
        self.year = str(year)
        self.week = str(week)
        # Use local storage directory for DigitalOcean
        self.download_folder = '/tmp/epo_patent'
        os.makedirs(self.download_folder, exist_ok=True)
        self.driver = None
        self.total_downloads = 0
        self.url_list = []

    def setYearWeek(self, year, week):
        self.year = str(year)
        self.week = str(week)

    def setup_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')
        options.add_argument('--disable-css')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-extensions')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # For DigitalOcean/Linux environments
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        
        # Use webdriver-manager to handle ChromeDriver installation
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            # Fallback to system ChromeDriver
            self.driver = webdriver.Chrome(options=options)
        
        return True

    def fill_and_search(self):
        self.driver.get('https://data.epo.org/publication-server/?lg=en')
        time.sleep(2)

        print(f"Start Searching for Year: {self.year}, Week: {self.week} ...")
        self.driver.execute_script("""
            const yearValue = arguments[0];
            const weekValue = arguments[1];
            const publicationDate = "During"

            async function clickDropdownAndSelect(labelPart, value) {
                return new Promise(resolve => {
                    const dropdown = document.querySelector('[aria-label*="' + labelPart + '"]');
                    if (!dropdown) {
                        console.warn(labelPart + ' dropdown not found');
                        return resolve(false);
                    }
                    dropdown.click();
                    setTimeout(() => {
                        const options = Array.from(document.querySelectorAll('[role="option"], li, div'));
                        const target = options.find(el => el.textContent.trim() === value);
                        if (target) {
                            target.click();
                            console.log('✅ ' + labelPart + ' set to ' + value);
                            resolve(true);
                        } else {
                            console.warn('❌ ' + labelPart + ' value "' + value + '" not found');
                            resolve(false);
                        }
                    }, 300);
                });
            }

            (async function run() {
                await clickDropdownAndSelect('Publication date', publicationDate);
                await clickDropdownAndSelect('Year', yearValue);
                await clickDropdownAndSelect('Week', weekValue);

                const searchBtn = document.querySelector('button[data-testid="search_button"], button[type="submit"]');
                if (searchBtn) searchBtn.click();
            })();
        """, self.year, self.week)

        print(f"🔍 Searching...")
        time.sleep(3)
        return True

    def get_all_zip_links(self):
        zip_data = self.driver.execute_script("""
            var zipLinks = [];
            var elements = document.querySelectorAll('a[href*=".zip"]');

            for (var i = 0; i < elements.length; i++) {
                var href = elements[i].href;
                if (href && href.includes('.zip')) {
                    var filename = href.split('/').pop().split('?')[0];
                    if (!filename.endsWith('.zip')) filename += '.zip';
                    zipLinks.push({url: href, filename: filename});
                }
            }
            return zipLinks;
        """)
        return zip_data

    def download_zip(self, url, filename):
        # Save URL instead of downloading
        self.url_list.append(url)
        return True

    def go_next_page(self):
        return self.driver.execute_script("""
            var nextElements = document.querySelectorAll('a, button');
            for (var i = 0; i < nextElements.length; i++) {
                var el = nextElements[i];
                var text = el.textContent.toLowerCase().trim();
                var href = el.href || '';
                var ariaLabel = (el.getAttribute('aria-label') || '').toLowerCase();

                if (el.offsetParent !== null && !el.disabled && !el.classList.contains('disabled')) {
                    if (text.includes('next') || text === '>' || text === '›' ||
                        href.includes('next') || ariaLabel.includes('next')) {
                        el.click();
                        return true;
                    }
                }
            }
            return false;
        """)

    def run(self):
        print("🚀 Ultra-Fast EPO ZIP Downloader Starting...", flush=True)

        if not self.setup_driver():
            return 0

        output_file = os.path.abspath(os.path.join(self.download_folder, f"{self.year}_{self.week}.txt"))

        try:
            if not self.fill_and_search():
                return 0

            page = 1

            with open(output_file, "w") as f:
                while page <= 4000000:
                    zip_links = self.get_all_zip_links()

                    if not zip_links:
                        if page > 1:
                            break
                        else:
                            page += 1
                            continue

                    print(f"Page {page}: {len(zip_links)} files", flush=True)

                    for link in zip_links:
                        self.download_zip(link['url'], link['filename'])
                        f.write(link['url'] + "\n")

                    if not self.go_next_page():
                        break

                    time.sleep(1)
                    page += 1

            print(f"\n✅ Complete! Saved URLs to:\n{output_file}\n", flush=True)
            return len(self.url_list)

        finally:
            if self.driver:
                self.driver.quit()

# Flask Routes
@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>EPO URL Downloader</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .form-group { margin: 20px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .result { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }
        .loading { display: none; text-align: center; }
        .files-list { max-height: 300px; overflow-y: auto; background: #f8f9fa; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 EPO URL Downloader</h1>
        <p>Extract ZIP file URLs from EPO patent database for specified year and week ranges.</p>
        
        <form id="downloadForm">
            <div class="form-group">
                <label>Year Start:</label>
                <input type="number" id="yearStart" value="2024" min="1979" max="2025">
            </div>
            <div class="form-group">
                <label>Year End:</label>
                <input type="number" id="yearEnd" value="2025" min="1979" max="2025">
            </div>
            <div class="form-group">
                <label>Week Start:</label>
                <input type="number" id="weekStart" value="1" min="1" max="52">
            </div>
            <div class="form-group">
                <label>Week End:</label>
                <input type="number" id="weekEnd" value="52" min="1" max="52">
            </div>
            <button type="submit">Start Download</button>
        </form>

        <div class="loading" id="loading">
            <p>🔄 Processing... This may take a while.</p>
        </div>

        <div id="result" class="result" style="display: none;"></div>
        
        <div id="files" style="display: none;">
            <h3>Generated Files:</h3>
            <div id="filesList" class="files-list"></div>
        </div>
    </div>

    <script>
        document.getElementById('downloadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const yearStart = document.getElementById('yearStart').value;
            const yearEnd = document.getElementById('yearEnd').value;
            const weekStart = document.getElementById('weekStart').value;
            const weekEnd = document.getElementById('weekEnd').value;
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            document.getElementById('files').style.display = 'none';
            
            fetch('/download', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    year_start: parseInt(yearStart),
                    year_end: parseInt(yearEnd),
                    week_start: parseInt(weekStart),
                    week_end: parseInt(weekEnd)
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').style.display = 'block';
                document.getElementById('result').innerHTML = 
                    '<h3>✅ Download Complete!</h3>' +
                    '<p>Status: ' + data.status + '</p>' +
                    '<p>Total Files Processed: ' + data.total_files + '</p>' +
                    '<p>Files Generated: ' + data.files_generated + '</p>';
                
                if (data.files && data.files.length > 0) {
                    document.getElementById('files').style.display = 'block';
                    document.getElementById('filesList').innerHTML = data.files.map(file => 
                        '<div><a href="/download_file/' + encodeURIComponent(file) + '" download>' + file + '</a></div>'
                    ).join('');
                }
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').style.display = 'block';
                document.getElementById('result').innerHTML = '<h3>❌ Error</h3><p>' + error + '</p>';
            });
        });
    </script>
</body>
</html>
    """)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    year_start = data.get('year_start', 2024)
    year_end = data.get('year_end', 2025)
    week_start = data.get('week_start', 1)
    week_end = data.get('week_end', 52)
    
    downloader = FastEPODownloader(year=year_start, week=week_start)
    total_files = 0
    generated_files = []
    
    try:
        for year in range(year_start, year_end):
            for week in range(week_start, week_end + 1):
                print(f"\n📅 Running for Year: {year}, Week: {week:02d}")
                downloader.setYearWeek(year, week)
                
                try:
                    result = downloader.run()
                    total_files += result
                    
                    # Check if file was created
                    filename = f"{year}_{week}.txt"
                    filepath = os.path.join(downloader.download_folder, filename)
                    if os.path.exists(filepath):
                        generated_files.append(filename)
                        
                except Exception as e:
                    print(f"❌ Error in Year {year}, Week {week}: {e}")
        
        return jsonify({
            'status': 'completed',
            'total_files': total_files,
            'files_generated': len(generated_files),
            'files': generated_files
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/download_file/<filename>')
def download_file(filename):
    from flask import send_from_directory
    return send_from_directory('/tmp/epo_patent', filename, as_attachment=True)

@app.route('/files')
def list_files():
    try:
        files = os.listdir('/tmp/epo_patent')
        files = [f for f in files if f.endswith('.txt')]
        return jsonify({'files': files})
    except:
        return jsonify({'files': []})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8088))
    print(f'🚀 EPO Downloader Server starting on port {port}')
    app.run(host='0.0.0.0', port=port, debug=False)
