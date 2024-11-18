let currentPage = 1;
let rowsPerPage = parseInt(document.getElementById('rowsPerPage').value);
let totalUrls = [];

// Listen for form submission
document.getElementById('scrapeForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    // Show the "Scraping..." loading indicator
    document.getElementById('loadingIndicator').style.display = 'block';
    // Scroll to the top of the page
    window.scrollTo({ top: 0});
    // Disable scrolling
    document.body.style.overflow = 'hidden';

    // Hide results and download buttons before scraping
    document.getElementById('results').style.display = 'none';
    document.getElementById('downloadCsv').style.display = 'none';
    document.getElementById('downloadExcel').style.display = 'none';
    document.getElementById('downloadPdf').style.display = 'none';

    // Reset URLs before scraping again
    totalUrls = [];

    const formData = new FormData(e.target);
    const response = await fetch('/scrape', {
        method: 'POST',
        body: formData,
    });

    const data = await response.json();

    if (data.urls) {
        totalUrls = data.urls;  // Store URLs for pagination
        renderTable(totalUrls, currentPage);  // Render first page of URLs

        // Show the total number of scraped URLs
        document.getElementById('totalCount').textContent = `Total URLs: ${totalUrls.length}`;

        // Show the results section and pagination
        document.getElementById('results').style.display = 'block';  // Make the results section visible

        // Show download buttons
        document.getElementById('downloadCsv').style.display = 'inline';
        document.getElementById('downloadExcel').style.display = 'inline';
        document.getElementById('downloadPdf').style.display = 'inline';

        // Update rows per page dynamically when changed
        document.getElementById('rowsPerPage').addEventListener('change', (event) => {
            rowsPerPage = parseInt(event.target.value);
            currentPage = 1; // Reset to first page on change
            renderTable(totalUrls, currentPage);  // Re-render from page 1
        });
    } else {
        alert(`Error: ${data.error}`);
    }

    // Hide the "Scraping..." indicator after scraping is done
    document.getElementById('loadingIndicator').style.display = 'none';

    // Re-enable scrolling after scraping is done
    document.body.style.overflow = 'auto';
});

// Function to render the table with pagination
function renderTable(urls, page) {
    const urlTable = document.getElementById('urlTable');
    const pagination = document.getElementById('pagination');
    urlTable.innerHTML = '';  // Clear previous table content

    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const paginatedUrls = urls.slice(start, end);

    // Populate the table with paginated URLs
    paginatedUrls.forEach((url) => {
        const row = urlTable.insertRow();
        const cell = row.insertCell(0);
        cell.textContent = url;
    });

    // Render pagination controls
    const totalPages = Math.ceil(urls.length / rowsPerPage);
    pagination.innerHTML = `
        <button id="firstPage" class="pagination-btn"><<</button>
        <button id="prevPage" class="pagination-btn"><</button>
        Page <input type="number" id="pageInput" value="${page}" min="1" max="${totalPages}"/> 
        of&nbsp;${totalPages}
        <button id="nextPage" class="pagination-btn">></button>
        <button id="lastPage" class="pagination-btn">>></button>
    `;

    // Event listeners for pagination buttons
    document.getElementById('firstPage').addEventListener('click', () => {
        currentPage = 1;
        renderTable(urls, currentPage);
    });
    document.getElementById('prevPage').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            renderTable(urls, currentPage);
        }
    });
    document.getElementById('nextPage').addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            renderTable(urls, currentPage);
        }
    });
    document.getElementById('lastPage').addEventListener('click', () => {
        currentPage = totalPages;
        renderTable(urls, currentPage);
    });
    document.getElementById('pageInput').addEventListener('change', (e) => {
        const inputPage = parseInt(e.target.value);
        if (inputPage >= 1 && inputPage <= totalPages) {
            currentPage = inputPage;
            renderTable(urls, currentPage);
        } else {
            e.target.value = currentPage; // Reset to current page if invalid
        }
    });
}

// Function to download CSV/Excel/PDF with all scraped URLs
async function downloadFile(type) {
    if (totalUrls.length === 0) {
        alert("No URLs to download.");
        return;
    }

    const response = await fetch('/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls: totalUrls, file_type: type }),
    });

    if (!response.ok) {
        alert("Failed to download file.");
        return;
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sitemap.${type}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
}

function showLoadingIndicator() {
    document.getElementById('loadingIndicator').style.display = 'flex';
}

function hideLoadingIndicator() {
    document.getElementById('loadingIndicator').style.display = 'none';
}

// Add event listeners to download buttons
document.getElementById('downloadCsv').addEventListener('click', () => downloadFile('csv'));
document.getElementById('downloadExcel').addEventListener('click', () => downloadFile('xlsx'));
document.getElementById('downloadPdf').addEventListener('click', () => downloadFile('pdf'));
