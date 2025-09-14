#!/usr/bin/env python3
"""
Main entry point for Railway - imports main_simple
"""

# Importar la aplicación desde main_simple
from main_simple import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
