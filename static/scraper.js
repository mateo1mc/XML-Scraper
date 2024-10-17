let currentPage = 1;
let rowsPerPage = parseInt(document.getElementById('rowsPerPage').value);  // Initial rows per page
let totalUrls = [];  // To store the fetched URLs

// Listen for form submission
document.getElementById('scrapeForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const response = await fetch('/scrape', {
        method: 'POST',
        body: formData,
    });

    const data = await response.json();

    if (data.urls) {
        totalUrls = data.urls;  // Store URLs for pagination
        renderTable(totalUrls, 1);  // Render first page of URLs
        document.getElementById('downloadCsv').style.display = 'inline';
        document.getElementById('downloadExcel').style.display = 'inline';

        // Update rows per page dynamically when changed
        document.getElementById('rowsPerPage').addEventListener('change', (event) => {
            rowsPerPage = parseInt(event.target.value);
            renderTable(totalUrls, 1);  // Re-render from page 1
        });
    } else {
        alert(`Error: ${data.error}`);
    }
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
        <button id="firstPage"><<</button>
        <button id="prevPage"><</button>
        Page <input type="number" id="pageInput" value="${page}" min="1" max="${totalPages}"/> of ${totalPages}
        <button id="nextPage">></button>
        <button id="lastPage">>></button>
    `;

    // Event listeners for pagination buttons
    document.getElementById('firstPage').addEventListener('click', () => renderTable(urls, 1));
    document.getElementById('prevPage').addEventListener('click', () => {
        if (page > 1) {
            renderTable(urls, page - 1);
        }
    });
    document.getElementById('nextPage').addEventListener('click', () => {
        if (page < totalPages) {
            renderTable(urls, page + 1);
        }
    });
    document.getElementById('lastPage').addEventListener('click', () => renderTable(urls, totalPages));
    document.getElementById('pageInput').addEventListener('change', (e) => {
        const inputPage = parseInt(e.target.value);
        if (inputPage >= 1 && inputPage <= totalPages) {
            renderTable(urls, inputPage);
        } else {
            e.target.value = page;  // Reset if input is invalid
        }
    });
}

// Function to download CSV/Excel with all scraped URLs
async function downloadFile(type) {
    if (totalUrls.length === 0) {
        alert("No URLs to download.");
        return;
    }

    const response = await fetch('/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls: totalUrls, file_type: type }),  // Send all URLs
    });

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sitemap.${type}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
}

// Add event listeners to download buttons
document.getElementById('downloadCsv').addEventListener('click', () => downloadFile('csv'));
document.getElementById('downloadExcel').addEventListener('click', () => downloadFile('xlsx'));
