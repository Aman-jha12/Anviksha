let allData = [];
let filteredData = [];
let currentFilters = {
    district: 'all',
    category: 'all',
    year: 'all'
};

// Load and initialize data
async function loadData() {
    try {
        const response = await fetch('data.csv');
        const csvText = await response.text();
        
        allData = parseCSV(csvText);
        filteredData = [...allData];
        
        populateFilters();
        applyFilters();
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

function parseCSV(text) {
    const lines = text.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    
    return lines.slice(1).map(line => {
        const values = line.split(',').map(v => v.trim());
        const row = {};
        headers.forEach((header, index) => {
            row[header] = values[index];
        });
        return row;
    });
}

function populateFilters() {
    // Populate districts
    const districts = [...new Set(allData.map(row => row.District))].sort();
    const districtFilter = document.getElementById('district-filter');
    districts.forEach(district => {
        const option = document.createElement('option');
        option.value = district;
        option.textContent = district;
        districtFilter.appendChild(option);
    });
    
    // Populate categories
    const categories = [...new Set(allData.map(row => row.Category))].sort();
    const categoryFilter = document.getElementById('category-filter');
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categoryFilter.appendChild(option);
    });
    
    // Populate years
    const years = [...new Set(allData.map(row => row.Year))].sort((a, b) => b - a);
    const yearFilter = document.getElementById('year-filter');
    years.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearFilter.appendChild(option);
    });
}

function applyFilters() {
    currentFilters.district = document.getElementById('district-filter').value;
    currentFilters.category = document.getElementById('category-filter').value;
    currentFilters.year = document.getElementById('year-filter').value;
    
    filteredData = allData.filter(row => {
        const matchDistrict = currentFilters.district === 'all' || row.District === currentFilters.district;
        const matchCategory = currentFilters.category === 'all' || row.Category === currentFilters.category;
        const matchYear = currentFilters.year === 'all' || row.Year === currentFilters.year;
        
        return matchDistrict && matchCategory && matchYear;
    });
    
    updateMetrics();
    updateStats();
    updateDataTable();
}

function updateMetrics() {
    const totalStudents = filteredData.reduce((sum, row) => sum + parseInt(row.Students || 0), 0);
    const totalSchools = new Set(filteredData.map(row => row.School)).size;
    const avgStudents = filteredData.length > 0 ? (totalStudents / filteredData.length).toFixed(1) : 0;
    
    document.getElementById('total-students').textContent = totalStudents.toLocaleString();
    document.getElementById('total-schools').textContent = totalSchools.toLocaleString();
    document.getElementById('avg-students').textContent = avgStudents;
}

function updateStats() {
    // District-wise distribution
    const districtData = {};
    filteredData.forEach(row => {
        const district = row.District;
        districtData[district] = (districtData[district] || 0) + parseInt(row.Students || 0);
    });
    
    createBarChart('district-chart', districtData, 'Students by District');
    
    // Category-wise distribution
    const categoryData = {};
    filteredData.forEach(row => {
        const category = row.Category;
        categoryData[category] = (categoryData[category] || 0) + parseInt(row.Students || 0);
    });
    
    createBarChart('category-chart', categoryData, 'Students by Category');
    
    // Year-wise trend
    const yearData = {};
    filteredData.forEach(row => {
        const year = row.Year;
        yearData[year] = (yearData[year] || 0) + parseInt(row.Students || 0);
    });
    
    createLineChart('trend-chart', yearData, 'Students Trend Over Years');
}

function updateDataTable() {
    const tbody = document.querySelector('#data-table tbody');
    tbody.innerHTML = '';
    
    const displayData = filteredData.slice(0, 100); // Show first 100 rows
    
    displayData.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.District || ''}</td>
            <td>${row.School || ''}</td>
            <td>${row.Category || ''}</td>
            <td>${row.Year || ''}</td>
            <td>${parseInt(row.Students || 0).toLocaleString()}</td>
        `;
        tbody.appendChild(tr);
    });
    
    // Update showing count
    document.getElementById('showing-count').textContent = 
        `Showing ${displayData.length} of ${filteredData.length} records`;
}

function createBarChart(canvasId, data, title) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    
    if (window[canvasId + 'Chart']) {
        window[canvasId + 'Chart'].destroy();
    }
    
    window[canvasId + 'Chart'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: title,
                data: Object.values(data),
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function createLineChart(canvasId, data, title) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    
    if (window[canvasId + 'Chart']) {
        window[canvasId + 'Chart'].destroy();
    }
    
    window[canvasId + 'Chart'] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Object.keys(data).sort(),
            datasets: [{
                label: title,
                data: Object.keys(data).sort().map(key => data[key]),
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

// Event listeners
document.getElementById('apply-filters').addEventListener('click', applyFilters);

// Initialize
loadData();
