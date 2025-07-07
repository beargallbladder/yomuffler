#!/usr/bin/env python3
"""
Ford Pro Fleet Risk Intelligence Dashboard
Quick Start Script

Run this to launch the executive dashboard demo
"""

import sys
import os
import subprocess

def main():
    print("🚀 Starting Ford Pro Fleet Risk Intelligence Dashboard...")
    print("📊 Executive Configuration & Real-Time Fleet Analysis")
    print("=" * 60)
    
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Import and run the dashboard
        from src.api.fleet_risk_dashboard import app
        
        print("✅ Dashboard API initialized")
        print("🌐 Starting web server...")
        print("\n🎯 Dashboard URL: http://localhost:5000/dashboard")
        print("📡 API Endpoints:")
        print("   • GET  /api/v1/stressor-configs")
        print("   • POST /api/v1/fleet-risk")
        print("   • GET  /api/v1/fleet-details/<risk_level>")
        print("\n💡 Executive Features:")
        print("   • Real-time stressor configuration")
        print("   • Live weather data integration")
        print("   • Interactive fleet risk visualization")
        print("   • Revenue opportunity calculation")
        print("\n🔥 Demo Instructions:")
        print("   1. Open http://localhost:5000/dashboard")
        print("   2. Toggle behavioral stressors in Executive Decision Center")
        print("   3. Watch fleet risk categories update in real-time")
        print("   4. See revenue opportunities change with each decision")
        print("\n" + "=" * 60)
        print("Press Ctrl+C to stop the dashboard")
        print("=" * 60)
        
        # Run the Flask app
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=False  # Disable reloader to avoid duplicate startup messages
        )
        
    except ImportError as e:
        print(f"❌ Error importing dashboard: {e}")
        print("📦 Installing required packages...")
        
        # Install required packages
        subprocess.run([sys.executable, "-m", "pip", "install", "flask", "flask-cors"])
        
        print("✅ Packages installed. Please run the script again.")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard stopped by user")
        print("👋 Thank you for using Ford Pro Fleet Risk Intelligence!")
        
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("🔧 Please check the error message above and try again.")

if __name__ == "__main__":
    main() 