# XML-Scraper

`XML-Scraper` is a web application built with Flask that allows users to scrape URLs from XML sitemaps. The application extracts URLs based on an XPath expression and supports optional regex filtering. It provides the ability to download the scraped data in CSV, Excel, or PDF formats.

## Features
- Extract URLs from XML sitemaps using XPath.
- Filter extracted URLs using a regex pattern.
- Paginate and preview extracted URLs.
- Download URLs in CSV, Excel, or PDF format.

## Requirements
- Python 3.x
- Flask
- requests
- pandas
- openpyxl
- reportlab

## Installation
1. Clone the repository:

   ```
   git clone https://github.com/mateo1mc/xml-scraper.git
   cd xml-scraper
   ```

2. Install the required Python packages:

   ```
   pip install -r requirements.txt
   ```

3. Start the Flask development server:

   ```
   python app.py
   ```

4. Visit http://127.0.0.1:5000 in your browser to use the application.

## Usage
1. Scraping URLs:

   - Enter the URL of the sitemap you want to scrape.
   - Provide an XPath expression to specify the location of the URLs in the XML (default is `.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc`).
   - Optionally, provide a regex pattern to filter the URLs.
   - Click the "Scrape" button to fetch and display the URLs.

2. Pagination:

   - The scraped URLs will be displayed in a table with pagination controls.
   - You can adjust the number of rows per page and navigate through the pages using the pagination buttons.

3. Download Options:

   Once the URLs are scraped, you can download them in one of the following formats:
   - CSV
   - Excel (XLSX)
   - PDF
   Click the corresponding download button to save the file.

## File Structure
      
      xml-scraper/
      │
      ├── app.py                # Main Flask application
      ├── requirements.txt      # Python dependencies
      ├── templates/
      │   └── index.html        # HTML template for the homepage
      ├── static/
      │   ├── scraper.js        # JavaScript for client-side interactions
      │   └── styles.css        # CSS for styling the application
      └── README.md             # Project documentation
      

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/mateo1mc/XML-Scraper/blob/46e0d2b93f3465bf34ea4ceae5b4779385c41279/LICENSE) file for details.


