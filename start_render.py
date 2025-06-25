#!/usr/bin/env python3
"""
Ford Risk Score Engine - Render Startup Script

This script initializes the Ford Risk Score Engine for Render deployment:
- Sets up environment variables
- Initializes database if needed
- Starts the API server with mobile interface
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def initialize_database():
    """Initialize database with basic schema"""
    try:
        import asyncpg
        
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.warning("No DATABASE_URL found, skipping database initialization")
            return
        
        logger.info("Initializing database...")
        
        # Connect to database
        conn = await asyncpg.connect(database_url)
        
        # Create basic tables if they don't exist
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS vehicle_risk_scores (
                vin VARCHAR(17) PRIMARY KEY,
                risk_score DECIMAL(5,4) NOT NULL,
                severity_bucket VARCHAR(20) NOT NULL,
                cohort VARCHAR(100) NOT NULL,
                dominant_stressors JSONB DEFAULT '[]',
                recommended_action TEXT NOT NULL,
                revenue_opportunity DECIMAL(10,2) DEFAULT 0,
                confidence DECIMAL(5,4) NOT NULL,
                scored_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours'),
                model_version VARCHAR(10) DEFAULT '1.0'
            );
        """)
        
        # Insert sample Bayesian priors
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS bayesian_priors (
                cohort_key VARCHAR(100) PRIMARY KEY,
                base_failure_rate DECIMAL(5,4) NOT NULL,
                sample_size INTEGER NOT NULL,
                source VARCHAR(50) NOT NULL
            );
        """)
        
        # Insert sample data
        await conn.execute("""
            INSERT INTO bayesian_priors (cohort_key, base_failure_rate, sample_size, source) VALUES
            ('F150|ICE|NORTH|LOW', 0.023, 15420, 'Argon National Study'),
            ('F150|ICE|NORTH|MEDIUM', 0.031, 12850, 'Argon National Study'),
            ('F150|ICE|NORTH|HIGH', 0.045, 8930, 'Argon National Study'),
            ('EXPLORER|ICE|NORTH|MEDIUM', 0.029, 7250, 'Argon National Study'),
            ('MUSTANG|ICE|NORTH|LOW', 0.018, 5420, 'Argon National Study')
            ON CONFLICT (cohort_key) DO NOTHING;
        """)
        
        await conn.close()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        # Don't fail startup if database init fails


def setup_environment():
    """Setup environment variables for Render"""
    
    # Set default environment
    os.environ.setdefault("ENVIRONMENT", "production")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    
    # Redis URL (if not set, will use in-memory fallback)
    if not os.getenv("REDIS_URL"):
        logger.warning("No REDIS_URL found, using in-memory cache fallback")
    
    # Port for Render
    port = os.getenv("PORT", "8000")
    os.environ["PORT"] = port
    
    logger.info(f"Environment setup complete. Port: {port}")


async def main():
    """Main startup function"""
    logger.info("🚀 Starting Ford Risk Score Engine on Render")
    
    # Setup environment
    setup_environment()
    
    # Initialize database
    await initialize_database()
    
    logger.info("✅ Initialization complete")


if __name__ == "__main__":
    # Run initialization
    asyncio.run(main())
    
    # Import and start the API
    from src.api.gateway import app
    
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"🌐 Starting Ford Risk Score Engine on port {port}")
    logger.info("📱 Mobile interface available at: /")
    logger.info("📖 API docs available at: /docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    ) 