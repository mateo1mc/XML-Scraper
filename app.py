from flask import Flask, request, render_template, jsonify, send_file
import requests
import re
import xml.etree.ElementTree as ET
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table
from requests.exceptions import RequestException, Timeout
from datetime import datetime
import gzip
import io

app = Flask(__name__)

# Route: Home Page
@app.route('/')
def home():
    current_year = datetime.now().year
    return render_template("index.html", current_year=current_year)

# Route: Extract URLs from Sitemap
@app.route('/scrape', methods=['POST'])
def scrape():
    sitemap_url = request.form['sitemap_url']
    xpath = request.form['xpath']
    regex = request.form['regex']

    try:
        # to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        }
        response = requests.get(sitemap_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Check if the content is gzipped
        if sitemap_url.endswith('.gz'):
            # Decompress the .gz content
            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as gz_file:
                decompressed_data = gz_file.read()
        else:
            decompressed_data = response.content

        # Parse XML Sitemap
        root = ET.fromstring(decompressed_data)
        urls = [elem.text for elem in root.findall(xpath)]

        # Filter URLs with Regex if provided
        if regex:
            pattern = re.compile(regex)
            urls = [url for url in urls if pattern.match(url)]

        return jsonify({'urls': urls})

    except Timeout:
        return jsonify({'error': 'The request timed out. Please try again later or check the URL.'}), 504
    except RequestException as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    except ET.ParseError as e:
        return jsonify({'error': f'Failed to parse XML: {str(e)}'}), 500
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

# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
