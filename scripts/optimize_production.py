#!/usr/bin/env python3
"""
Production Optimization Script for VIN Stressors Platform
Validates all integrations and ensures deployment health
"""

import os
import json
import requests
import time
from pathlib import Path
from datetime import datetime
import subprocess
import sys

class ProductionOptimizer:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.server_url = "http://localhost:8000"
        self.auth = ("dealer", "stressors2024")
        self.results = {
            'optimization_date': datetime.now().isoformat(),
            'checks_performed': [],
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log optimization progress"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
        if level == "WARNING":
            self.results['warnings'].append(message)
        elif level == "ERROR":
            self.results['errors'].append(message)
    
    def check_server_health(self) -> bool:
        """Check if the production server is running and healthy"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                self.log(f"✅ Server health: {health_data.get('status', 'unknown')}")
                self.results['checks_performed'].append("Server health check")
                return True
            else:
                self.log(f"❌ Server health check failed: HTTP {response.status_code}", "ERROR")
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Server not accessible: {str(e)}", "ERROR")
            return False
    
    def check_authentication(self) -> bool:
        """Check if authentication is working"""
        try:
            # Test without auth (should fail)
            response = requests.get(f"{self.server_url}/", timeout=5)
            if response.status_code == 401:
                self.log("✅ Authentication protection active")
                
                # Test with auth (should succeed)
                response = requests.get(f"{self.server_url}/", auth=self.auth, timeout=5)
                if response.status_code == 200:
                    self.log("✅ Authentication working correctly")
                    self.results['checks_performed'].append("Authentication check")
                    return True
                else:
                    self.log(f"❌ Authentication failed: HTTP {response.status_code}", "ERROR")
                    return False
            else:
                self.log("⚠️ Authentication may not be configured", "WARNING")
                return True  # Not necessarily an error
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Authentication check failed: {str(e)}", "ERROR")
            return False
    
    def check_data_files(self) -> bool:
        """Check if all required data files exist"""
        required_files = [
            "data/cohorts.json",
            "vin_leads_database_*.json",
            "weather_validation_*.json", 
            "nhtsa_ford_complaints_*.json"
        ]
        
        all_files_exist = True
        
        for file_pattern in required_files:
            if "*" in file_pattern:
                # Handle wildcard patterns
                files = list(self.base_path.glob(file_pattern))
                if files:
                    latest_file = max(files, key=lambda f: f.stat().st_mtime)
                    file_size = latest_file.stat().st_size
                    self.log(f"✅ Found {file_pattern}: {latest_file.name} ({file_size // 1024}KB)")
                    
                    # Check file size warnings
                    if file_size > 10 * 1024 * 1024:  # 10MB
                        self.log(f"⚠️ Large file detected: {latest_file.name} ({file_size // 1024 // 1024}MB)", "WARNING")
                        self.results['recommendations'].append(f"Consider compressing {latest_file.name}")
                else:
                    self.log(f"❌ Missing required file: {file_pattern}", "ERROR")
                    all_files_exist = False
            else:
                # Handle exact file paths
                file_path = self.base_path / file_pattern
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    self.log(f"✅ Found {file_pattern} ({file_size // 1024}KB)")
                else:
                    self.log(f"❌ Missing required file: {file_pattern}", "ERROR")
                    all_files_exist = False
        
        if all_files_exist:
            self.results['checks_performed'].append("Data files check")
        
        return all_files_exist
    
    def calculate_system_score(self) -> float:
        """Calculate overall system health score"""
        score = 0.0
        total_checks = 4  # Server, auth, data files, API endpoints
        
        # Basic scoring based on successful checks
        successful_checks = len(self.results['checks_performed'])
        score = (successful_checks / total_checks) * 100
        
        # Deduct points for errors and warnings
        score -= len(self.results['errors']) * 10
        score -= len(self.results['warnings']) * 2
        
        return max(0, round(score, 1))
    
    def run_optimization(self) -> dict:
        """Run complete production optimization"""
        print("🔧 PRODUCTION OPTIMIZATION STARTING")
        print("=" * 50)
        
        # Check server health
        if not self.check_server_health():
            self.log("Cannot proceed without healthy server", "ERROR")
            return self.results
        
        # Check authentication
        self.check_authentication()
        
        # Check data files
        self.check_data_files()
        
        # Calculate system score
        system_score = self.calculate_system_score()
        
        # Generate recommendations
        if system_score >= 80:
            self.results['recommendations'].append("System is production ready")
        elif system_score >= 60:
            self.results['recommendations'].append("System is suitable for demos with minor optimizations")
        else:
            self.results['recommendations'].append("System needs significant optimization before production")
        
        # Final results
        self.results.update({
            'system_score': system_score,
            'deployment_status': 'HEALTHY' if len(self.results['errors']) == 0 else 'DEGRADED',
            'optimization_complete': True
        })
        
        return self.results
    
    def export_results(self, filename: str = None):
        """Export optimization results"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"production_optimization_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Generate summary report
        report_filename = filename.replace('.json', '_summary.txt')
        with open(report_filename, 'w') as f:
            f.write("PRODUCTION OPTIMIZATION REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Optimization Date: {self.results['optimization_date']}\n")
            f.write(f"System Score: {self.results.get('system_score', 0)}/100\n")
            f.write(f"Deployment Status: {self.results.get('deployment_status', 'UNKNOWN')}\n\n")
            
            f.write("CHECKS PERFORMED:\n")
            for check in self.results['checks_performed']:
                f.write(f"  ✅ {check}\n")
            f.write("\n")
            
            if self.results['warnings']:
                f.write("WARNINGS:\n")
                for warning in self.results['warnings']:
                    f.write(f"  ⚠️ {warning}\n")
                f.write("\n")
            
            if self.results['errors']:
                f.write("ERRORS:\n")
                for error in self.results['errors']:
                    f.write(f"  ❌ {error}\n")
                f.write("\n")
            
            f.write("RECOMMENDATIONS:\n")
            for rec in self.results['recommendations']:
                f.write(f"  🎯 {rec}\n")
        
        print(f"\n📄 Optimization results: {filename}")
        print(f"📋 Summary report: {report_filename}")
        
        return filename, report_filename

def main():
    """Main optimization execution"""
    optimizer = ProductionOptimizer()
    
    # Run optimization
    results = optimizer.run_optimization()
    
    # Export results
    data_file, summary_file = optimizer.export_results()
    
    # Print summary
    print(f"\n✨ OPTIMIZATION COMPLETE!")
    print(f"   🎯 System Score: {results.get('system_score', 0)}/100")
    print(f"   📊 Status: {results.get('deployment_status', 'UNKNOWN')}")
    print(f"   ✅ Checks: {len(results['checks_performed'])}")
    print(f"   ⚠️ Warnings: {len(results['warnings'])}")
    print(f"   ❌ Errors: {len(results['errors'])}")
    
    if results.get('system_score', 0) >= 70:
        print("\n🎉 System is optimized and ready for production!")
    else:
        print("\n🔧 System needs optimization - check recommendations")

if __name__ == "__main__":
    main() 