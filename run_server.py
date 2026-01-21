import uvicorn

if __name__ == "__main__":
    print("\n🚀 Starting Anviksha server with auto-reload...")
    print("📂 Data location: sample_data/west_bengal_road_tenders_sample.csv")
    print("🌐 Open: http://localhost:8000")
    print("⚠️  CACHE DISABLED - Changes appear immediately")
    print("🔄 AUTO-RELOAD ENABLED\n")
    
    uvicorn.run(
        "app:app",  # Important: string import for reload
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
