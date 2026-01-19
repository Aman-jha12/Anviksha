# Anviksha

**Public Infrastructure Spending Explorer**

A transparency-focused web portal for exploring publicly available government procurement data, specifically focusing on road construction tenders in West Bengal, India.

## Overview

Anviksha is a public transparency and research portal designed to enable exploration of government infrastructure spending patterns. The application provides statistical analysis, visualizations, and detailed data exploration without making accusations or claims of wrongdoing.

### Core Identity

- **NOT** a commercial SaaS product
- **NOT** a political tool
- **NOT** an accusation system
- **IS** a public transparency & research portal

**Tone**: Neutral, calm, informational, research-grade, anonymous

## Features

- 📊 **Preloaded Dataset**: Representative subset of publicly available West Bengal road construction data
- 📈 **Inflation Adjustment**: All values adjusted to 2024 prices using Indian CPI
- 🔍 **Interactive Exploration**: Filter by district and department using HTMX
- 📉 **Visual Analytics**: Charts showing spending patterns, vendor analysis, and trends
- 🔬 **Statistical Observations**: Neutral pattern detection using standard methods
- 📥 **Data Export**: Download summary and detailed CSV reports
- 🎨 **Clean UI**: Public data portal design (not SaaS dashboard)

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Server-rendered HTML with Jinja2 templates
- **Interactivity**: HTMX (no heavy JavaScript frameworks)
- **Data Processing**: Pandas, NumPy
- **Analysis**: Scikit-learn (simple, explainable methods)
- **Visualization**: Matplotlib (server-generated charts)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Anviksha
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload
   ```

4. **Access the application**:
   Open your browser and navigate to `http://localhost:8000`

## Dataset

The application uses a preloaded dataset containing 20 road construction tenders from West Bengal (2019-2024). The dataset includes:

- Tender IDs
- Districts (Howrah, Kolkata, Burdwan, Nadia, Malda, Paschim Medinipur)
- Departments (PWD)
- Road types (Rural, Urban, State Highway)
- Project lengths
- Vendor names
- Tender values (in crores)
- Award years
- Bidder counts

**Data Source**: Representative subset of publicly available government procurement data.

## Usage

### Main Interface

1. **Header**: Site title and tagline
2. **Disclaimer**: Transparency notice and ethical framework
3. **Explorer Controls**: Filter by district and department (updates dynamically via HTMX)
4. **Overview**: High-level statistics (total spending, projects, time range, avg cost/km)
5. **Visual Exploration**: Charts showing:
   - Spending by district
   - Spending over time
   - Top vendors by contract value
6. **Statistical Observations**: Notable patterns detected using neutral language
7. **Detailed Table**: Complete tender information with inflation-adjusted values
8. **Export**: Download data as CSV

### Filtering

Select a district or department from the dropdown menus. The page updates automatically without full reload using HTMX.

### Export

- **Summary CSV**: District-level spending summary
- **Detailed CSV**: Complete tender data with all calculated fields

## Methodology

### Inflation Adjustment

All contract values are adjusted for inflation using India's Consumer Price Index (CPI):

```
Adjusted_Value = Original_Value × (CPI_base_year / CPI_contract_year)
```

- Base Year: 2024
- CPI Data: Uses official Indian CPI data from RBI/Ministry of Statistics
- Purpose: Allows fair comparison of contracts across different years

### Statistical Analysis

The application uses standard statistical methods:

- **Percentile Analysis**: Identifies high-cost outliers
- **Interquartile Range (IQR)**: Detects unusual patterns
- **Vendor Concentration**: Measures contract distribution
- **Year-over-Year Comparison**: Identifies trends

### Language & Framing

All observations use neutral, research-grade language:

- "Unusual statistical pattern"
- "Requires further review"
- "Notable observation"
- "May reflect changes in project scope"

**Never uses**: Accusatory language, claims of wrongdoing, or political targeting.

## Project Structure

```
Anviksha/
├── main.py                    # FastAPI backend
├── data.py                    # Data loading and preprocessing
├── inflation_adjustment.py    # CPI-based inflation adjustment
├── analysis.py               # Statistical analysis
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── templates/
│   ├── index.html            # Main page template
│   └── partials/
│       └── results.html      # HTMX partial for results
└── static/
    └── style.css             # CSS styling
```

## Privacy & Anonymity

- **No login required**
- **No authentication**
- **No user tracking**
- **No personal data storage**
- **No cookies** (except session cookies for HTMX)
- **Anonymous usage**

## Limitations

1. **Dataset Scope**: Uses a representative subset (20 tenders), not complete coverage
2. **Geographic Scope**: West Bengal only
3. **Sector Scope**: Road construction only
4. **CPI Data**: Uses approximate CPI values (for production, integrate with official API)
5. **No Live Data**: Does not scrape or fetch live data from government portals

## Ethical Considerations

- **Neutral Framing**: Results are framed as statistical observations
- **Transparency**: All methods are documented and explainable
- **Research Focus**: Designed for transparency and research, not litigation
- **No Targeting**: Tool does not target specific parties or organizations
- **Public Data Only**: Uses only publicly available information

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Adding New Data

To add new data, modify the `PRELOADED_DATA` string in `data.py` with CSV-formatted data.

### Customizing Analysis

Modify functions in `analysis.py` to add new statistical methods or observations.

## License

This project is intended for research and transparency purposes. Please use responsibly and in accordance with applicable laws and regulations.

## Disclaimer

**This portal provides access to publicly available government procurement data for transparency and research purposes. It does not determine intent or wrongdoing. All analysis is based on statistical methods and presents observations for further review.**

The application must NEVER:
- Use words like "corruption", "scam", "fraud"
- Target any political party
- Name individuals or organizations as guilty
- Claim complete or live data coverage

Results are always framed as "statistical patterns requiring further review."

---

**Built for transparency. Designed for research. Anonymous usage.**
