#!/usr/bin/env python3
"""
Ford Bayesian Risk Score Engine - Production Entry Point
Simplified for Render deployment
"""

import os
import sys
import logging

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Start the Ford Bayesian Risk Score Engine"""
    try:
        logger.info("🚀 Starting Ford Bayesian Risk Score Engine")
        logger.info(f"📁 Working directory: {os.getcwd()}")
        logger.info(f"🐍 Python path: {sys.path[:3]}")  # Show first 3 entries
        
        # Import after path setup
        import uvicorn
        
        # Get configuration from environment
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 8000))
        
        logger.info(f"🌐 Starting server on {host}:{port}")
        
        # Create a simple FastAPI app for testing
        from fastapi import FastAPI
        from fastapi.responses import HTMLResponse
        
        app = FastAPI(title="Ford Risk Score Engine")
        
        @app.get("/")
        async def root():
            return HTMLResponse("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Ford Risk Score Engine</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>🚗 Ford Risk Score Engine</h1>
                <p>Academic-backed vehicle intelligence system</p>
                <p>✅ Deployment successful!</p>
                <p>🎯 Ready for cohort-based risk scoring</p>
            </body>
            </html>
            """)
        
        @app.get("/health")
        async def health():
            return {"status": "healthy", "service": "ford-risk-engine"}
        
        # Start the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 