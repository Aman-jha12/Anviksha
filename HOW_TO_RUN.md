# How to Run Anviksha

## Step-by-Step Instructions

### Option 1: Using the Quick Start Script (Recommended)

1. **Open Terminal/PowerShell** in the Anviksha directory

2. **Activate virtual environment** (if you have one):
   ```bash
   # Windows PowerShell
   .\venv\Scripts\Activate.ps1
   
   # Windows CMD
   venv\Scripts\activate.bat
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python run.py
   ```

5. **Open your browser** and go to:
   ```
   http://localhost:8000
   ```

### Option 2: Using Python main.py directly

```bash
python main.py
```

### Option 3: Using uvicorn directly

```bash
uvicorn main:app --reload
```

## What You Should See

When the server starts, you'll see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Then open `http://localhost:8000` in your browser.

## Troubleshooting

### Port Already in Use
If port 8000 is busy, change it:
```bash
uvicorn main:app --reload --port 8001
```

### Module Not Found Errors
Install missing dependencies:
```bash
pip install fastapi uvicorn jinja2 python-multipart pandas numpy scikit-learn matplotlib
```

### Charts Not Showing
Ensure matplotlib is installed:
```bash
pip install matplotlib
```

## Quick Test

Once running, you should see:
- ✅ Header with "Anviksha" title
- ✅ Disclaimer panel
- ✅ Filter dropdowns (District, Department)
- ✅ Overview statistics cards
- ✅ Charts (3 visualizations)
- ✅ Statistical observations
- ✅ Detailed tender table
- ✅ Export buttons

## Stopping the Server

Press `Ctrl+C` in the terminal to stop the server.
