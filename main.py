"""
Anviksha - FastAPI Backend

Public Infrastructure Spending Explorer
A transparency-focused portal for exploring government procurement data.
"""

import logging
import traceback
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import json
import base64
from io import BytesIO
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import modules
try:
    logger.info("Importing data module...")
    from data import load_preloaded_data, get_filtered_data, get_unique_values
    logger.info("✓ data module imported")
except ImportError as e:
    logger.error(f"❌ Failed to import data module: {e}")
    raise

try:
    logger.info("Importing inflation_adjustment module...")
    from inflation_adjustment import apply_inflation_adjustment
    logger.info("✓ inflation_adjustment module imported")
except ImportError as e:
    logger.error(f"❌ Failed to import inflation_adjustment module: {e}")
    raise

try:
    logger.info("Importing analysis module...")
    from analysis import (
        calculate_statistics,
        spending_by_district,
        spending_by_year,
        vendor_analysis,
        detect_statistical_observations,
        calculate_cost_per_km,
        generate_insight_summary
    )
    logger.info("✓ analysis module imported")
except ImportError as e:
    logger.error(f"❌ Failed to import analysis module: {e}")
    raise

class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all errors with full context."""
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"❌ MIDDLEWARE ERROR on {request.method} {request.url.path}")
            logger.error(f"Error: {type(e).__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

# Initialize FastAPI
app = FastAPI(
    title="Anviksha",
    description="Public Infrastructure Spending Explorer",
    version="1.0.0"
)

# Add error middleware
app.add_middleware(ErrorLoggingMiddleware)

# Templates and static files
try:
    logger.info("Setting up templates...")
    templates = Jinja2Templates(directory="templates")
    
    # Add custom Jinja2 filters
    def median_filter(values):
        """Calculate median of a list of numbers."""
        if not values:
            return 0
        sorted_values = sorted(values)
        n = len(sorted_values)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_values[mid - 1] + sorted_values[mid]) / 2
        return sorted_values[mid]
    
    templates.env.filters['median'] = median_filter
    
    logger.info("✓ Templates loaded")
except Exception as e:
    logger.error(f"❌ Failed to load templates: {e}")
    raise

try:
    logger.info("Mounting static files...")
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("✓ Static files mounted")
except Exception as e:
    logger.error(f"❌ Failed to mount static files: {e}")
    raise

# Load data on startup
try:
    logger.info("Loading preloaded dataset...")
    raw_data = load_preloaded_data()
    logger.info(f"✓ Raw data loaded: {len(raw_data)} records")
    
    logger.info("Applying inflation adjustment...")
    processed_data = apply_inflation_adjustment(raw_data)
    logger.info(f"✓ Data processed: {len(processed_data)} records")
    
    logger.info("Extracting unique values...")
    unique_values = get_unique_values(processed_data)
    logger.info(f"✓ Unique districts: {len(unique_values['districts'])}")
    logger.info(f"✓ Unique departments: {len(unique_values['departments'])}")
except Exception as e:
    logger.error(f"❌ Failed to load/process data: {e}")
    logger.error(traceback.format_exc())
    raise


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page - explorer interface."""
    try:
        logger.info("GET / - Rendering index page")
        
        # Get default filtered data (all)
        logger.debug("Filtering data...")
        filtered_data = get_filtered_data(processed_data)
        logger.debug(f"Filtered data: {len(filtered_data)} records")
        
        logger.debug("Calculating statistics...")
        stats = calculate_statistics(filtered_data)
        logger.debug(f"Stats calculated: {stats.keys()}")
        
        # Get spending breakdowns
        logger.debug("Calculating spending by district...")
        district_spending = spending_by_district(filtered_data)
        logger.debug(f"Districts: {len(district_spending)}")
        
        logger.debug("Calculating spending by year...")
        year_spending = spending_by_year(filtered_data)
        logger.debug(f"Years: {len(year_spending)}")
        
        logger.debug("Calculating vendor analysis...")
        vendor_stats = vendor_analysis(filtered_data)
        logger.debug(f"Vendors: {len(vendor_stats)}")
        
        # Get observations
        logger.debug("Detecting observations...")
        observations = detect_statistical_observations(filtered_data)
        logger.debug(f"Observations: {len(observations)}")
        
        # Prepare detailed table data
        logger.debug("Calculating cost per km...")
        table_data = calculate_cost_per_km(filtered_data.copy())
        logger.debug(f"Table data rows: {len(table_data)}")
        
        # Generate charts
        logger.debug("Generating charts...")
        district_chart = generate_district_chart(district_spending)
        year_chart = generate_year_chart(year_spending)
        vendor_chart = generate_vendor_chart(vendor_stats.head(10))
        logger.debug("Charts generated")
        
        # Generate insight summary
        insight_summary = generate_insight_summary(filtered_data)
        # Fallback to stats-based summary if empty
        if not insight_summary or not str(insight_summary).strip():
            insight_summary = (
                f"For across all districts between {stats['time_range']}, total inflation-adjusted spending was "
                f"₹{stats['total_spending']/1_00_00_000:.2f} crore across {stats['total_projects']} project(s). "
                f"Average cost per km was ₹{stats['avg_cost_per_km']:.2f} lakh."
            )
        
        logger.info("✓ Index page rendered successfully")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "stats": stats,
            "districts": unique_values['districts'],
            "departments": unique_values['departments'],
            "district_spending": district_spending.to_dict('records'),
            "year_spending": year_spending.to_dict('records'),
            "vendor_stats": vendor_stats.head(10).to_dict('records'),
            "observations": observations,
            "table_data": table_data.to_dict('records'),
            "district_chart": district_chart,
            "year_chart": year_chart,
            "vendor_chart": vendor_chart,
            "insight_summary": insight_summary
        })
    except Exception as e:
        logger.error(f"❌ Error in index route: {e}")
        logger.error(traceback.format_exc())
        raise


@app.post("/filter", response_class=HTMLResponse)
async def filter_data(request: Request, district: str = Form("All"), department: str = Form("All")):
    """HTMX endpoint for filtering data."""
    try:
        logger.info(f"POST /filter - District: {district}, Department: {department}")
        
        filtered_data = get_filtered_data(processed_data, district, department)
        logger.debug(f"Filtered records: {len(filtered_data)}")
        
        stats = calculate_statistics(filtered_data)
        district_spending = spending_by_district(filtered_data)
        year_spending = spending_by_year(filtered_data)
        vendor_stats = vendor_analysis(filtered_data)
        observations = detect_statistical_observations(filtered_data)
        table_data = calculate_cost_per_km(filtered_data.copy())
        
        # Generate insight summary with filter context
        insight_summary = generate_insight_summary(
            filtered_data, 
            district if district != "All" else None,
            department if department != "All" else None
        )
        # Fallback to stats-based summary if empty
        if not insight_summary or not str(insight_summary).strip():
            insight_summary = (
                f"For {(district if district!='All' else 'all districts')}"
                f"{(', ' + department) if department!='All' else ''} between {stats['time_range']}, "
                f"total inflation-adjusted spending was ₹{stats['total_spending']/1_00_00_000:.2f} crore across "
                f"{stats['total_projects']} project(s). Average cost per km was ₹{stats['avg_cost_per_km']:.2f} lakh."
            )
        
        # Generate charts from filtered datasets (ensures charts reflect selection)
        district_chart = generate_district_chart(district_spending)
        year_chart = generate_year_chart(year_spending)
        vendor_chart = generate_vendor_chart(vendor_stats.head(10))
        
        logger.info("✓ Filter applied successfully")
        return templates.TemplateResponse("partials/results.html", {
            "request": request,
            "stats": stats,
            "district_spending": district_spending.to_dict('records'),
            "year_spending": year_spending.to_dict('records'),
            "vendor_stats": vendor_stats.head(10).to_dict('records'),
            "observations": observations,
            "table_data": table_data.to_dict('records'),
            "district_chart": district_chart,
            "year_chart": year_chart,
            "vendor_chart": vendor_chart,
            "insight_summary": insight_summary
        })
    except Exception as e:
        logger.error(f"❌ Error in filter route: {e}")
        logger.error(traceback.format_exc())
        raise


@app.get("/export/summary")
async def export_summary():
    """Export summary statistics as CSV."""
    try:
        logger.info("GET /export/summary")
        filtered_data = get_filtered_data(processed_data)
        district_spending = spending_by_district(filtered_data)
        
        csv = district_spending.to_csv(index=False)
        logger.info("✓ Summary exported")
        return Response(
            content=csv,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=anviksha_summary.csv"}
        )
    except Exception as e:
        logger.error(f"❌ Error in export_summary: {e}")
        logger.error(traceback.format_exc())
        raise


@app.get("/export/detailed")
async def export_detailed():
    """Export detailed tender data as CSV."""
    try:
        logger.info("GET /export/detailed")
        filtered_data = get_filtered_data(processed_data)
        detailed = calculate_cost_per_km(filtered_data)
        
        # Select relevant columns
        export_cols = [
            'Tender_ID', 'District', 'Department', 'Road_Type', 'Project_Length_km',
            'Vendor_Name', 'Tender_Value_Cr', 'Tender_Value_Adjusted_Rs',
            'Award_Year', 'Bidders_Count', 'Cost_Per_Km'
        ]
        
        csv = detailed[export_cols].to_csv(index=False)
        logger.info("✓ Detailed data exported")
        return Response(
            content=csv,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=anviksha_detailed.csv"}
        )
    except Exception as e:
        logger.error(f"❌ Error in export_detailed: {e}")
        logger.error(traceback.format_exc())
        raise


def generate_district_chart(df: pd.DataFrame) -> str:
    """Generate base64 encoded chart for district spending (sorted descending)."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        # Sort by spending descending
        df_sorted = df.sort_values('Total_Spending', ascending=True)  # ascending for barh to show largest at top
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(df_sorted['District'], df_sorted['Total_Spending'] / 1_00_00_000, color='#2563eb')
        ax.set_xlabel('Total Spending (₹ Cr)', fontsize=11, fontweight='600')
        ax.set_ylabel('District', fontsize=11, fontweight='600')
        ax.set_title('Spending by District (Inflation-Adjusted)', fontsize=13, fontweight='bold')
        ax.grid(axis='x', alpha=0.2, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return img_base64
    except Exception as e:
        logger.error(f"Chart generation error: {e}")
        logger.error(traceback.format_exc())
        return ""


def generate_year_chart(df: pd.DataFrame) -> str:
    """Generate base64 encoded chart for year-over-year spending."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df['Award_Year'], df['Total_Spending'] / 1_00_00_000, 
                marker='o', linewidth=3, markersize=8, color='#2563eb')
        ax.fill_between(df['Award_Year'], df['Total_Spending'] / 1_00_00_000, 
                         alpha=0.2, color='#2563eb')
        ax.set_xlabel('Year', fontsize=11, fontweight='600')
        ax.set_ylabel('Total Spending (₹ Cr)', fontsize=11, fontweight='600')
        ax.set_title('Spending Over Time (Inflation-Adjusted)', fontsize=13, fontweight='bold')
        ax.grid(alpha=0.2, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return img_base64
    except Exception as e:
        logger.error(f"Chart generation error: {e}")
        logger.error(traceback.format_exc())
        return ""


def generate_vendor_chart(df: pd.DataFrame) -> str:
    """Generate base64 encoded chart for top 5 vendors."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        # Limit to top 5 vendors
        df_top5 = df.head(5).sort_values('Total_Value', ascending=True)  # ascending for barh
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(df_top5['Vendor_Name'], df_top5['Total_Value'] / 1_00_00_000, color='#059669')
        ax.set_xlabel('Total Contract Value (₹ Cr)', fontsize=11, fontweight='600')
        ax.set_ylabel('Vendor', fontsize=11, fontweight='600')
        ax.set_title('Top 5 Vendors by Contract Value', fontsize=13, fontweight='bold')
        ax.grid(axis='x', alpha=0.2, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return img_base64
    except Exception as e:
        logger.error(f"Chart generation error: {e}")
        logger.error(traceback.format_exc())
        return ""


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global error handler for debugging."""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
