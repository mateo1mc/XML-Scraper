from flask import Flask, request, render_template, jsonify, send_file
import requests
import re
import xml.etree.ElementTree as ET
import pandas as pd
import os

app = Flask(__name__)

# Route: Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Route: Extract URLs from Sitemap
@app.route('/scrape', methods=['POST'])
def scrape():
    sitemap_url = request.form['sitemap_url']
    xpath = request.form['xpath']
    regex = request.form['regex']

    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()

        # Parse XML Sitemap
        root = ET.fromstring(response.content)
        urls = [elem.text for elem in root.findall(xpath)]

        # Filter URLs with Regex if provided
        if regex:
            pattern = re.compile(regex)
            urls = [url for url in urls if pattern.match(url)]

        return jsonify({'urls': urls})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route: Download as CSV/Excel
@app.route('/download', methods=['POST'])
def download():
    urls = request.json.get('urls')
    file_type = request.form['file_type']

    # Save URLs into a DataFrame
    df = pd.DataFrame(urls, columns=['URL'])

    # Generate filename dynamically
    filename = f'sitemap.{file_type}'
    filepath = os.path.join(os.getcwd(), filename)

    # Save as CSV or Excel
    if file_type == 'csv':
        df.to_csv(filepath, index=False)
    elif file_type == 'xlsx':
        df.to_excel(filepath, index=False)

    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
