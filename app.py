"""
Anviksha - Main FastAPI Application
"""

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
import pandas as pd
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import traceback
import time

# Custom middleware to disable caching
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # AGGRESSIVE CACHE BUSTING
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, post-check=0, pre-check=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        response.headers['X-Accel-Expires'] = '0'
        response.headers['ETag'] = f'"{hash(str(time.time()))}"'  # Add unique ETag
        response.headers['Last-Modified'] = 'Mon, 01 Jan 2024 00:00:00 GMT'
        print(f"🔄 Cache-busting headers set for: {request.url.path}")
        return response

app = FastAPI()
app.add_middleware(NoCacheMiddleware)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
templates.env.auto_reload = True

def load_data():
    """Load ALL data from CSV - FORCE ALL 72 ROWS"""
    csv_path = Path("sample_data/west_bengal_road_tenders_sample.csv")
    
    if not csv_path.exists():
        print(f"❌ CSV file not found at {csv_path}")
        return pd.DataFrame()
    
    # Load ALL rows - NO limiting whatsoever
    df = pd.read_csv(csv_path)
    print(f"📂 RAW CSV loaded: {len(df)} rows")
    
    # Verify all 72 rows
    if len(df) != 72:
        print(f"⚠️ WARNING: Expected 72 rows but got {len(df)}")
    
    # Print first and last Tender_ID
    if len(df) > 0:
        print(f"🔍 First Tender_ID: {df['Tender_ID'].iloc[0]}")
        print(f"🔍 Last Tender_ID: {df['Tender_ID'].iloc[-1]}")
        print(f"📋 All Tender_IDs: {df['Tender_ID'].tolist()[:5]}...{df['Tender_ID'].tolist()[-5:]}")
    
    # Clean data
    df['Award_Year'] = pd.to_numeric(df['Award_Year'], errors='coerce')
    df = df.dropna(subset=['Award_Year'])
    df['Award_Year'] = df['Award_Year'].astype(int)
    
    print(f"✅ After cleaning: {len(df)} rows (should still be 72)")
    
    # Clean data
    df['Project_Length_km'] = pd.to_numeric(df['Project_Length_km'], errors='coerce').fillna(0)
    df['Tender_Value_Adjusted_Rs'] = pd.to_numeric(df['Tender_Value_Adjusted_Rs'], errors='coerce').fillna(0)
    
    for col in ['District', 'Department', 'Vendor_Name', 'Road_Type', 'Project_Name']:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown').astype(str).str.strip()
    
    if 'Bidders_Count' in df.columns:
        df['Bidders_Count'] = pd.to_numeric(df['Bidders_Count'], errors='coerce').fillna(0).astype(int)
    else:
        df['Bidders_Count'] = 0
    
    df = df[df['Award_Year'] > 2000]
    df = df[df['Tender_Value_Adjusted_Rs'] > 0]
    
    print(f"✅ DATA LOADED: {len(df)} rows")
    return df

def calculate_stats(df):
    """Calculate statistics"""
    if df.empty:
        return {
            'total_spending': 0,
            'total_projects': 0,
            'avg_cost_per_km': 0,
            'districts_count': 0,
            'time_range': 'N/A'
        }
    
    total_spending = float(df['Tender_Value_Adjusted_Rs'].sum())
    total_projects = len(df)
    total_length = float(df['Project_Length_km'].sum())
    avg_cost_per_km = (total_spending / total_length) if total_length > 0 else 0
    districts_count = int(df['District'].nunique())
    
    years = sorted(df['Award_Year'].unique())
    time_range = f"{years[0]}-{years[-1]}" if len(years) > 1 else str(years[0]) if years else 'N/A'
    
    return {
        'total_spending': total_spending,
        'total_projects': total_projects,
        'avg_cost_per_km': avg_cost_per_km,
        'districts_count': districts_count,
        'time_range': time_range
    }

def detect_patterns(df):
    """Detect statistical patterns"""
    observations = []
    if df.empty or len(df) < 10:
        return observations
    
    try:
        q3 = df['Tender_Value_Adjusted_Rs'].quantile(0.75)
        q1 = df['Tender_Value_Adjusted_Rs'].quantile(0.25)
        iqr = q3 - q1
        outlier_threshold = q3 + 1.5 * iqr
        median_value = df['Tender_Value_Adjusted_Rs'].median()
        
        high_cost = df[df['Tender_Value_Adjusted_Rs'] > outlier_threshold]
        
        for _, row in high_cost.head(5).iterrows():
            ratio = row['Tender_Value_Adjusted_Rs'] / median_value if median_value > 0 else 1
            percentile = (df['Tender_Value_Adjusted_Rs'] <= row['Tender_Value_Adjusted_Rs']).sum() / len(df) * 100
            
            observations.append({
                'type': 'high_cost',
                'title': 'High-Value Project Detected',
                'description': f"Project '{row['Project_Name']}' in {row['District']} has a value of ₹{row['Tender_Value_Adjusted_Rs']/10000000:.2f} Cr ({ratio:.1f}× median)",
                'confidence': 'High',
                'confidence_reason': 'IQR method',
                'does_not_imply': 'Inefficiency. May reflect project complexity.'
            })
    except Exception as e:
        print(f"Error detecting patterns: {e}")
    
    return observations

def generate_year_chart(df):
    """Generate year chart"""
    if df.empty:
        return ""
    try:
        yearly = df.groupby('Award_Year')['Tender_Value_Adjusted_Rs'].sum().sort_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(yearly.index, yearly.values / 10000000, marker='o', linewidth=2, color='#3b82f6')
        ax.set_xlabel('Year')
        ax.set_ylabel('Spending (₹ Cr)')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return img
    except:
        return ""

def generate_district_chart(df):
    """Generate district chart"""
    if df.empty:
        return ""
    try:
        district = df.groupby('District')['Tender_Value_Adjusted_Rs'].sum().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(district.index, district.values / 10000000, color='#10b981')
        ax.set_xlabel('Spending (₹ Cr)')
        ax.set_ylabel('District')
        ax.invert_yaxis()
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return img
    except:
        return ""

def generate_vendor_chart(df):
    """Generate vendor chart"""
    if df.empty:
        return ""
    try:
        vendor = df.groupby('Vendor_Name')['Tender_Value_Adjusted_Rs'].sum().sort_values(ascending=False).head(5)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(vendor.index, vendor.values / 10000000, color='#f59e0b')
        ax.set_xlabel('Value (₹ Cr)')
        ax.set_ylabel('Vendor')
        ax.invert_yaxis()
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return img
    except:
        return ""

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    timestamp = str(int(time.time()))
    print("\n" + "="*50)
    print(f"🏠 HOME PAGE LOAD - Timestamp: {timestamp}")
    print("="*50)
    
    df = load_data()
    print(f"📂 CSV loaded: {len(df)} rows")
    
    # Convert ALL 72 rows
    table_data = df.to_dict('records')
    print(f"✅ Converted {len(table_data)} rows")
    print(f"🔍 First: {table_data[0]['Tender_ID']}")
    print(f"🔍 Last: {table_data[-1]['Tender_ID']}")
    
    stats = calculate_stats(df)
    observations = detect_patterns(df)
    
    year_chart = generate_year_chart(df)
    district_chart = generate_district_chart(df)
    vendor_chart = generate_vendor_chart(df)
    
    year_spending = df.groupby('Award_Year')['Tender_Value_Adjusted_Rs'].sum().reset_index().rename(columns={'Tender_Value_Adjusted_Rs': 'Total_Spending'}).to_dict('records') if not df.empty else []
    district_spending = df.groupby('District')['Tender_Value_Adjusted_Rs'].sum().reset_index().rename(columns={'Tender_Value_Adjusted_Rs': 'Total_Spending'}).sort_values('Total_Spending', ascending=False).to_dict('records') if not df.empty else []
    vendor_stats = df.groupby('Vendor_Name')['Tender_Value_Adjusted_Rs'].sum().reset_index().nlargest(5, 'Tender_Value_Adjusted_Rs').rename(columns={'Tender_Value_Adjusted_Rs': 'Total_Value'}).to_dict('records') if not df.empty else []
    
    districts = ['all'] + sorted(df['District'].unique().tolist())
    departments = ['all'] + sorted(df['Department'].unique().tolist())
    years = ['all'] + sorted(df['Award_Year'].unique().tolist(), reverse=True)
    
    context = {
        "request": request,
        "table_data": table_data,
        "stats": stats,
        "observations": observations,
        "year_chart": year_chart,
        "district_chart": district_chart,
        "vendor_chart": vendor_chart,
        "year_spending": year_spending,
        "district_spending": district_spending,
        "vendor_stats": vendor_stats,
        "districts": districts,
        "departments": departments,
        "years": years,
        "selected_filters": None,
        "cache_bust": timestamp  # Force reload
    }
    
    response = templates.TemplateResponse("index.html", context)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Total-Rows'] = str(len(table_data))
    response.headers['X-Timestamp'] = timestamp
    
    print(f"✨ Sending {len(table_data)} rows with timestamp {timestamp}")
    print("="*50 + "\n")
    
    return response

@app.post("/filter", response_class=HTMLResponse)
async def filter_data(request: Request, district: str = Form(...), department: str = Form(...), year: str = Form("all")):
    """Filter data"""
    print("\n" + "="*50)
    print("🔽 FILTER REQUEST")
    print(f"📍 District: {district}, Department: {department}, Year: {year}")
    
    df = load_data()
    print(f"📊 Loaded {len(df)} rows")
    
    if district != "all":
        df = df[df['District'] == district]
        print(f"  → After district: {len(df)} rows")
    
    if department != "all":
        df = df[df['Department'] == department]
        print(f"  → After department: {len(df)} rows")
    
    if year != "all":
        df = df[df['Award_Year'] == int(year)]
        print(f"  → After year: {len(df)} rows")
    
    # Convert ALL filtered rows
    table_data = df.to_dict('records')
    print(f"✅ Returning {len(table_data)} rows")
    
    stats = calculate_stats(df)
    observations = detect_patterns(df)
    
    year_chart = generate_year_chart(df)
    district_chart = generate_district_chart(df)
    vendor_chart = generate_vendor_chart(df)
    
    year_spending = df.groupby('Award_Year')['Tender_Value_Adjusted_Rs'].sum().reset_index().rename(columns={'Tender_Value_Adjusted_Rs': 'Total_Spending'}).to_dict('records') if not df.empty else []
    district_spending = df.groupby('District')['Tender_Value_Adjusted_Rs'].sum().reset_index().rename(columns={'Tender_Value_Adjusted_Rs': 'Total_Spending'}).sort_values('Total_Spending', ascending=False).to_dict('records') if not df.empty else []
    vendor_stats = df.groupby('Vendor_Name')['Tender_Value_Adjusted_Rs'].sum().reset_index().nlargest(5, 'Tender_Value_Adjusted_Rs').rename(columns={'Tender_Value_Adjusted_Rs': 'Total_Value'}).to_dict('records') if not df.empty else []
    
    context = {
        "request": request,
        "table_data": table_data,
        "stats": stats,
        "observations": observations,
        "year_chart": year_chart,
        "district_chart": district_chart,
        "vendor_chart": vendor_chart,
        "year_spending": year_spending,
        "district_spending": district_spending,
        "vendor_stats": vendor_stats,
        "selected_filters": {'district': district, 'department': department, 'year': year}
    }
    
    print("="*50 + "\n")
    return templates.TemplateResponse("partials/results.html", context)

@app.get("/export/summary")
async def export_summary():
    """Export summary CSV"""
    df = load_data()
    if df.empty:
        return StreamingResponse(iter(["No data\n"]), media_type="text/csv")
    
    summary = df.groupby(['District', 'Department', 'Award_Year']).agg({
        'Tender_ID': 'count',
        'Tender_Value_Adjusted_Rs': ['sum', 'mean'],
        'Project_Length_km': 'sum'
    }).reset_index()
    
    summary.columns = ['District', 'Department', 'Award_Year', 'Total_Projects', 'Total_Spending_Rs', 'Avg_Value_Rs', 'Total_Length_Km']
    summary['Total_Spending_Cr'] = (summary['Total_Spending_Rs'] / 10000000).round(2)
    summary['Avg_Value_Cr'] = (summary['Avg_Value_Rs'] / 10000000).round(2)
    summary = summary[['District', 'Department', 'Award_Year', 'Total_Projects', 'Total_Spending_Cr', 'Avg_Value_Cr', 'Total_Length_Km']]
    
    stream = io.StringIO()
    summary.to_csv(stream, index=False)
    stream.seek(0)
    
    return StreamingResponse(iter([stream.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=summary.csv"})

@app.get("/export/detailed")
async def export_detailed():
    """Export detailed CSV"""
    df = load_data()
    if df.empty:
        return StreamingResponse(iter(["No data\n"]), media_type="text/csv")
    
    export_df = df.copy()
    export_df['Tender_Value_Cr'] = (export_df['Tender_Value_Adjusted_Rs'] / 10000000).round(2)
    export_df['Cost_Per_Km_Lakh'] = ((export_df['Tender_Value_Adjusted_Rs'] / export_df['Project_Length_km']) / 100000).round(2) if export_df['Project_Length_km'].sum() > 0 else 0
    
    export_cols = ['Tender_ID', 'Award_Year', 'District', 'Department', 'Project_Name', 'Vendor_Name', 'Project_Length_km', 'Tender_Value_Cr', 'Cost_Per_Km_Lakh', 'Bidders_Count', 'Road_Type']
    export_df = export_df[export_cols]
    
    stream = io.StringIO()
    export_df.to_csv(stream, index=False)
    stream.seek(0)
    
    return StreamingResponse(iter([stream.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=detailed.csv"})

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting Anviksha server...")
    print("🌐 Open: http://localhost:8000")
    print("🔄 AUTO-RELOAD ENABLED\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", reload=True)