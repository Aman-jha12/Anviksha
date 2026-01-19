"""
Quick start script for Anviksha
"""

import uvicorn

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🛣️  ANVIKSHA - Public Infrastructure Spending Explorer")
    print("="*60)
    print("📊 Transparent data analysis of road infrastructure spending")
    print("🌐 Access: http://localhost:8000")
    print("="*60 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
