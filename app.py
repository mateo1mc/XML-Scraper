from flask import Flask, request, render_template, jsonify, send_file
import requests
import re
import xml.etree.ElementTree as ET
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table

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

# Route: Download as CSV/Excel/PDF
@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()  # Read incoming JSON data
    urls = data.get('urls')
    file_type = data.get('file_type')

    # Validate the input
    if not urls or not file_type:
        return jsonify({'error': 'Invalid input'}), 400

    # Handle CSV and Excel in memory
    if file_type in ['csv', 'xlsx']:
        # Save URLs into a DataFrame
        df = pd.DataFrame(urls, columns=['URL'])

        # Save as CSV or Excel to a BytesIO object
        buffer = BytesIO()
        try:
            if file_type == 'csv':
                df.to_csv(buffer, index=False)
                buffer.seek(0)  # Rewind the buffer to the beginning
                return send_file(buffer, as_attachment=True, download_name='sitemap.csv', mimetype='text/csv')
            elif file_type == 'xlsx':
                df.to_excel(buffer, index=False, engine='openpyxl')  # Specify the engine here
                buffer.seek(0)  # Rewind the buffer to the beginning
                return send_file(buffer, as_attachment=True, download_name='sitemap.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif file_type == 'pdf':
        # Generate PDF
        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)

        # Create a table with the URLs
        table_data = [["URLs"]]  # Header
        table_data.extend([[url] for url in urls])  # Add URLs to table

        # Create the table without styling
        table = Table(table_data)

        # Build the PDF
        pdf.build([table])
        buffer.seek(0)

        # Send the PDF file as an attachment
        return send_file(buffer, as_attachment=True, download_name='sitemap.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
