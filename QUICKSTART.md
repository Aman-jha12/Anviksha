# Quick Start Guide - Anviksha

## Installation & Running

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python run.py
   ```
   
   Or directly:
   ```bash
   python main.py
   ```
   
   Or with uvicorn:
   ```bash
   uvicorn main:app --reload
   ```

3. **Access the application**:
   Open your browser to: `http://localhost:8000`

## What You'll See

1. **Header**: "Anviksha - Public Infrastructure Spending Explorer"
2. **Disclaimer Panel**: Transparency notice
3. **Filter Controls**: District and Department dropdowns (updates dynamically)
4. **Overview Cards**: Total spending, projects, time range, avg cost/km
5. **Charts**: Three visualizations (district spending, year trends, top vendors)
6. **Statistical Observations**: Neutral pattern detection results
7. **Detailed Table**: Complete tender data with inflation-adjusted values
8. **Export Buttons**: Download CSV files

## Key Features

- ✅ Preloaded dataset (20 tenders from West Bengal)
- ✅ Inflation adjustment to 2024 prices
- ✅ HTMX-powered dynamic filtering (no page reload)
- ✅ Server-generated charts (Matplotlib)
- ✅ Statistical pattern detection
- ✅ CSV export functionality
- ✅ Clean, public data portal design
- ✅ No login, no tracking, anonymous usage

## File Structure

```
Anviksha/
├── main.py                    # FastAPI backend
├── run.py                     # Quick start script
├── data.py                    # Data loading
├── inflation_adjustment.py    # CPI adjustment
├── analysis.py                # Statistical analysis
├── requirements.txt           # Dependencies
├── templates/
│   ├── index.html            # Main page
│   └── partials/
│       └── results.html      # HTMX partial
└── static/
    └── style.css             # CSS styling
```

## Testing

The application loads with 20 preloaded tenders. Use the dropdown filters to:
- Filter by district (Howrah, Kolkata, Burdwan, etc.)
- Filter by department (PWD)
- See results update instantly via HTMX

## Troubleshooting

- **Port already in use**: Change port in `run.py` or use `--port 8001`
- **Charts not showing**: Ensure matplotlib is installed correctly
- **HTMX not working**: Check browser console, ensure HTMX CDN loads

## Next Steps

- Modify `data.py` to add more tenders
- Customize `analysis.py` for different statistical methods
- Update `static/style.css` for custom styling
- Add more filter options in `main.py`
