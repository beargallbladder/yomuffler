#!/usr/bin/env python3
"""
Ford Bayesian Risk Score Engine - Production Entry Point
Academic cohort-based risk scoring with Argonne ANL-115925.pdf validation
"""

import os
import sys
import logging
import uvicorn
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api.gateway import app

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Start the Ford Bayesian Risk Score Engine"""
    logger.info("🚀 Starting Ford Bayesian Risk Score Engine - Academic Cohort System")
    logger.info("📚 Powered by Argonne ANL-115925.pdf validation")
    logger.info("🎯 Version 1.1 - Academic cohort integration")
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    # Log startup configuration
    logger.info(f"🌐 Starting server on {host}:{port}")
    logger.info(f"📁 Working directory: {os.getcwd()}")
    logger.info(f"🐍 Python version: {sys.version}")
    
    # Store startup time for health checks
    app.state.start_time = datetime.utcnow().timestamp()
    
    # Start the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        server_header=False,
        date_header=False
    )

if __name__ == "__main__":
    main() 