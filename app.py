from flask import Flask, request, render_template, jsonify, send_file
import requests
import re
import xml.etree.ElementTree as ET
import pandas as pd
from io import BytesIO

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
    data = request.get_json()  # Read incoming JSON data
    urls = data.get('urls')
    file_type = data.get('file_type')

    # Validate the input
    if not urls or not file_type:
        return jsonify({'error': 'Invalid input'}), 400

    # Save URLs into a DataFrame
    df = pd.DataFrame(urls, columns=['URL'])

    # Create an in-memory file for CSV or Excel
    output = BytesIO()

    # Save as CSV or Excel to the in-memory file
    try:
        if file_type == 'csv':
            df.to_csv(output, index=False)
            output.seek(0)  # Move to the beginning of the BytesIO object
            return send_file(output, mimetype='text/csv', as_attachment=True, download_name='sitemap.csv')
        elif file_type == 'xlsx':
            df.to_excel(output, index=False, engine='openpyxl')  # Specify the engine here
            output.seek(0)  # Move to the beginning of the BytesIO object
            return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='sitemap.xlsx')
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
