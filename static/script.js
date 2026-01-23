// Configure Plotly defaults
Plotly.setPlotConfig({
    responsive: true,
    displayModeBar: false
});

// Global chart styling
const chartLayout = {
    margin: { t: 20, b: 40, l: 60, r: 20 },
    plot_bgcolor: '#f9fafb',
    paper_bgcolor: '#ffffff',
    font: {
        family: 'system-ui, -apple-system, sans-serif',
        size: 12,
        color: '#374151'
    },
    xaxis: {
        showgrid: true,
        gridwidth: 1,
        gridcolor: '#e5e7eb',
        zeroline: false
    },
    yaxis: {
        showgrid: true,
        gridwidth: 1,
        gridcolor: '#e5e7eb',
        zeroline: false
    }
};

// Wait for Plotly to load
document.addEventListener('DOMContentLoaded', function() {
    console.log('✓ Anviksha portal initialized');
    
    // COUNT TABLE ROWS ON LOAD
    countTableRows();
    
    // Initialize table interactions
    initializeTableInteractions();
    setupTableSearch();
});

// HTMX Event Listeners
document.addEventListener('htmx:beforeRequest', function(evt) {
    console.log('🔄 HTMX request starting...', evt.detail);
    const formData = new FormData(evt.detail.elt);
    console.log('📋 Form data:', {
        district: formData.get('district'),
        department: formData.get('department'),
        year: formData.get('year')
    });
});

document.addEventListener('htmx:afterRequest', function(evt) {
    console.log('✅ HTMX request completed', evt.detail.xhr.status);
    if (evt.detail.xhr.status === 200) {
        console.log('✓ Filters applied successfully');
        
        // COUNT ROWS AFTER UPDATE
        setTimeout(() => {
            countTableRows();
        }, 100);
        
        // Smooth scroll to results
        setTimeout(() => {
            const resultsContainer = document.getElementById('results-container');
            if (resultsContainer) {
                resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }, 100);
    }
});

document.addEventListener('htmx:responseError', function(evt) {
    console.error('HTMX error:', evt.detail);
    alert('Error updating filters. Please try again.');
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Cmd/Ctrl + K for filter focus
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        const districtSelect = document.getElementById('district');
        if (districtSelect) {
            districtSelect.focus();
        }
    }
});

// Currency formatter utility
function formatCurrency(value) {
    if (value >= 10000000) {
        return '₹' + (value / 10000000).toFixed(2) + ' Cr';
    } else if (value >= 100000) {
        return '₹' + (value / 100000).toFixed(2) + ' L';
    }
    return '₹' + value.toFixed(0);
}

function initializeTableInteractions() {
    const tableRows = document.querySelectorAll('.data-row');
    const searchInput = document.getElementById('table-search');

    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('keyup', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            tableRows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }

    // Row click expansion (optional future enhancement)
    tableRows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Visual feedback only - no modal
            this.classList.toggle('is-active');
        });
    });

    // Research note interactions
    const researchNotes = document.querySelectorAll('.research-note');
    researchNotes.forEach(note => {
        note.addEventListener('mouseenter', function() {
            // Highlight corresponding table row
            const tenderId = this.dataset.patternType;
            const correspondingRows = document.querySelectorAll(`[data-tender-id]`);
            correspondingRows.forEach(row => {
                if (row.textContent.includes(tenderId)) {
                    row.classList.add('is-highlighted');
                }
            });
        });

        note.addEventListener('mouseleave', function() {
            const correspondingRows = document.querySelectorAll('.is-highlighted');
            correspondingRows.forEach(row => {
                row.classList.remove('is-highlighted');
            });
        });
    });
}

// Table search functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded, initializing...');
    setupTableSearch();
});

// Re-setup search after HTMX swap
document.body.addEventListener('htmx:afterSwap', function(event) {
    console.log('HTMX swap detected');
    if (event.detail.target.id === 'results-container') {
        setupTableSearch();
    }
});

function setupTableSearch() {
    const searchInput = document.getElementById('table-search');
    if (!searchInput) {
        console.log('Search input not found');
        return;
    }
    
    console.log('Setting up table search');
    
    // Remove existing listeners
    const newSearchInput = searchInput.cloneNode(true);
    searchInput.parentNode.replaceChild(newSearchInput, searchInput);
    
    newSearchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase().trim();
        const tableBody = document.getElementById('table-body');
        
        if (!tableBody) {
            console.log('Table body not found');
            return;
        }
        
        const rows = tableBody.getElementsByTagName('tr');
        let visibleCount = 0;
        
        for (let row of rows) {
            // Skip the "no data" row
            if (row.cells.length === 1) continue;
            
            const text = row.textContent.toLowerCase();
            if (searchTerm === '' || text.includes(searchTerm)) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        }
        
        console.log(`Search: "${searchTerm}" - ${visibleCount} rows visible`);
    });
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// NEW FUNCTION: Count and log table rows
function countTableRows() {
    const tableBody = document.getElementById('table-body');
    if (!tableBody) {
        console.warn('⚠️ Table body not found');
        return;
    }
    
    const allRows = tableBody.querySelectorAll('tr');
    const dataRows = tableBody.querySelectorAll('tr.data-row');
    
    console.log('\n' + '='.repeat(50));
    console.log('📊 TABLE ROW COUNT');
    console.log('='.repeat(50));
    console.log(`Total <tr> elements: ${allRows.length}`);
    console.log(`Data rows (.data-row): ${dataRows.length}`);
    console.log(`First row text: ${dataRows[0]?.textContent.substring(0, 50)}...`);
    console.log(`Last row text: ${dataRows[dataRows.length - 1]?.textContent.substring(0, 50)}...`);
    console.log('='.repeat(50) + '\n');
    
    // Also check the table meta count
    const tableMeta = document.querySelector('.table-meta strong');
    if (tableMeta) {
        console.log(`📋 Meta count shows: ${tableMeta.textContent} projects`);
    }
}
