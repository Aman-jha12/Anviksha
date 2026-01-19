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
    
    // Initialize table interactions
    initializeTableInteractions();
});

// HTMX Event Listeners
document.addEventListener('htmx:beforeRequest', function(evt) {
    console.log('Filter request initiated');
});

document.addEventListener('htmx:afterRequest', function(evt) {
    if (evt.detail.xhr.status === 200) {
        console.log('✓ Filters applied successfully');
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
    console.error('Filter error:', evt.detail.error);
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
