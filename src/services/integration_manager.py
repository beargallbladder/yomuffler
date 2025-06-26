#!/usr/bin/env python3
"""
Integration Manager for VIN Stressors Platform
Combines lead database, weather validation, and NHTSA data
Optimized for production deployment with caching and performance
"""

import json
import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
from functools import lru_cache

class IntegrationManager:
    """Centralized manager for all data integrations"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent
        self.data_cache = {}
        self.cache_expiry = {}
        self.cache_duration = timedelta(hours=6)  # Cache for 6 hours
        
        # Integration status tracking
        self.integration_status = {
            'lead_database': {'status': 'unknown', 'last_check': None, 'count': 0},
            'weather_validation': {'status': 'unknown', 'last_check': None, 'accuracy': 'unknown'},
            'nhtsa_complaints': {'status': 'unknown', 'last_check': None, 'count': 0},
            'cohort_data': {'status': 'unknown', 'last_check': None, 'count': 4}
        }
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache_expiry:
            return False
        return datetime.now() < self.cache_expiry[key]
    
    def _set_cache(self, key: str, data: any) -> None:
        """Set data in cache with expiry"""
        self.data_cache[key] = data
        self.cache_expiry[key] = datetime.now() + self.cache_duration
    
    @lru_cache(maxsize=128)
    def get_latest_file(self, pattern: str, directory: str = ".") -> Optional[str]:
        """Get the most recent file matching pattern"""
        try:
            search_path = self.base_path / directory
            files = list(search_path.glob(pattern))
            if not files:
                return None
            # Sort by modification time, most recent first
            latest_file = max(files, key=lambda f: f.stat().st_mtime)
            return str(latest_file)
        except Exception as e:
            self.logger.error(f"Error finding latest file {pattern}: {str(e)}")
            return None
    
    def load_lead_database(self) -> Dict:
        """Load the latest lead database with caching"""
        cache_key = 'lead_database'
        
        if self._is_cache_valid(cache_key):
            return self.data_cache[cache_key]
        
        try:
            # Find latest lead database file
            latest_file = self.get_latest_file("vin_leads_database_*.json")
            
            if not latest_file:
                self.integration_status['lead_database'] = {
                    'status': 'error', 
                    'last_check': datetime.now().isoformat(),
                    'count': 0,
                    'error': 'No lead database file found'
                }
                return {'error': 'No lead database found'}
            
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            # Update integration status
            lead_count = len(data.get('leads', []))
            self.integration_status['lead_database'] = {
                'status': 'active',
                'last_check': datetime.now().isoformat(),
                'count': lead_count,
                'file': os.path.basename(latest_file),
                'total_revenue': data.get('summary', {}).get('total_revenue_opportunity', 0)
            }
            
            self._set_cache(cache_key, data)
            self.logger.info(f"Loaded lead database: {lead_count} leads")
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading lead database: {str(e)}")
            self.integration_status['lead_database'] = {
                'status': 'error',
                'last_check': datetime.now().isoformat(),
                'count': 0,
                'error': str(e)
            }
            return {'error': str(e)}
    
    def load_weather_validation(self) -> Dict:
        """Load weather validation data with caching"""
        cache_key = 'weather_validation'
        
        if self._is_cache_valid(cache_key):
            return self.data_cache[cache_key]
        
        try:
            # Find latest weather validation file
            latest_file = self.get_latest_file("weather_validation_*.json")
            
            if not latest_file:
                self.integration_status['weather_validation'] = {
                    'status': 'error',
                    'last_check': datetime.now().isoformat(),
                    'accuracy': 'unknown',
                    'error': 'No weather validation file found'
                }
                return {'error': 'No weather validation found'}
            
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            # Update integration status
            validation_data = data.get('validation_results', {})
            accuracy_assessment = validation_data.get('accuracy_assessment', {})
            
            self.integration_status['weather_validation'] = {
                'status': 'active',
                'last_check': datetime.now().isoformat(),
                'accuracy': accuracy_assessment.get('overall_accuracy', 'unknown'),
                'max_error': accuracy_assessment.get('max_average_error', 0),
                'locations': accuracy_assessment.get('total_comparisons', 0),
                'file': os.path.basename(latest_file)
            }
            
            self._set_cache(cache_key, data)
            self.logger.info(f"Loaded weather validation: {accuracy_assessment.get('overall_accuracy', 'unknown')} accuracy")
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading weather validation: {str(e)}")
            self.integration_status['weather_validation'] = {
                'status': 'error',
                'last_check': datetime.now().isoformat(),
                'accuracy': 'unknown',
                'error': str(e)
            }
            return {'error': str(e)}
    
    def load_nhtsa_complaints(self) -> Dict:
        """Load NHTSA complaint data with caching"""
        cache_key = 'nhtsa_complaints'
        
        if self._is_cache_valid(cache_key):
            return self.data_cache[cache_key]
        
        try:
            # Find latest NHTSA complaint file
            latest_file = self.get_latest_file("nhtsa_ford_complaints_*.json")
            
            if not latest_file:
                self.integration_status['nhtsa_complaints'] = {
                    'status': 'error',
                    'last_check': datetime.now().isoformat(),
                    'count': 0,
                    'error': 'No NHTSA complaint file found'
                }
                return {'error': 'No NHTSA complaints found'}
            
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            # Update integration status
            complaint_count = data.get('total_battery_complaints', 0)
            analysis = data.get('analysis', {})
            
            self.integration_status['nhtsa_complaints'] = {
                'status': 'active',
                'last_check': datetime.now().isoformat(),
                'count': complaint_count,
                'batches_processed': data.get('batches_processed', 0),
                'geographic_coverage': len(analysis.get('geographic_distribution', {})),
                'file': os.path.basename(latest_file)
            }
            
            self._set_cache(cache_key, data)
            self.logger.info(f"Loaded NHTSA complaints: {complaint_count} battery-related")
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading NHTSA complaints: {str(e)}")
            self.integration_status['nhtsa_complaints'] = {
                'status': 'error',
                'last_check': datetime.now().isoformat(),
                'count': 0,
                'error': str(e)
            }
            return {'error': str(e)}
    
    def load_cohort_data(self) -> Dict:
        """Load cohort configuration data"""
        cache_key = 'cohort_data'
        
        if self._is_cache_valid(cache_key):
            return self.data_cache[cache_key]
        
        try:
            cohort_file = self.base_path / "data" / "cohorts.json"
            
            if not cohort_file.exists():
                self.integration_status['cohort_data'] = {
                    'status': 'error',
                    'last_check': datetime.now().isoformat(),
                    'count': 0,
                    'error': 'No cohort data file found'
                }
                return {'error': 'No cohort data found'}
            
            with open(cohort_file, 'r') as f:
                data = json.load(f)
            
            # Update integration status
            cohort_count = len(data.get('cohorts', {}))
            
            self.integration_status['cohort_data'] = {
                'status': 'active',
                'last_check': datetime.now().isoformat(),
                'count': cohort_count,
                'file': 'cohorts.json'
            }
            
            self._set_cache(cache_key, data)
            self.logger.info(f"Loaded cohort data: {cohort_count} cohorts")
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading cohort data: {str(e)}")
            self.integration_status['cohort_data'] = {
                'status': 'error',
                'last_check': datetime.now().isoformat(),
                'count': 0,
                'error': str(e)
            }
            return {'error': str(e)}
    
    def get_integration_status(self) -> Dict:
        """Get comprehensive status of all integrations"""
        # Refresh all integration statuses
        self.load_lead_database()
        self.load_weather_validation()
        self.load_nhtsa_complaints()
        self.load_cohort_data()
        
        # Calculate overall system health
        active_integrations = sum(1 for status in self.integration_status.values() 
                                if status['status'] == 'active')
        total_integrations = len(self.integration_status)
        
        system_health = {
            'overall_status': 'healthy' if active_integrations == total_integrations else 'degraded',
            'active_integrations': active_integrations,
            'total_integrations': total_integrations,
            'health_percentage': round((active_integrations / total_integrations) * 100, 1),
            'last_check': datetime.now().isoformat()
        }
        
        return {
            'system_health': system_health,
            'integrations': self.integration_status,
            'cache_status': {
                'cached_items': len(self.data_cache),
                'cache_hit_potential': len([k for k in self.data_cache.keys() if self._is_cache_valid(k)])
            }
        }
    
    def get_combined_intelligence(self) -> Dict:
        """Get combined business intelligence from all integrations"""
        try:
            # Load all data sources
            leads = self.load_lead_database()
            weather = self.load_weather_validation()
            nhtsa = self.load_nhtsa_complaints()
            cohorts = self.load_cohort_data()
            
            # Combine intelligence
            intelligence = {
                'data_sources': {
                    'lead_database': {
                        'status': 'available' if 'error' not in leads else 'unavailable',
                        'lead_count': len(leads.get('leads', [])) if 'error' not in leads else 0,
                        'revenue_opportunity': leads.get('summary', {}).get('total_revenue_opportunity', 0) if 'error' not in leads else 0
                    },
                    'weather_validation': {
                        'status': 'available' if 'error' not in weather else 'unavailable',
                        'accuracy': weather.get('validation_results', {}).get('accuracy_assessment', {}).get('overall_accuracy', 'unknown') if 'error' not in weather else 'unknown',
                        'locations_validated': weather.get('validation_results', {}).get('accuracy_assessment', {}).get('total_comparisons', 0) if 'error' not in weather else 0
                    },
                    'nhtsa_validation': {
                        'status': 'available' if 'error' not in nhtsa else 'unavailable',
                        'complaint_count': nhtsa.get('total_battery_complaints', 0) if 'error' not in nhtsa else 0,
                        'geographic_coverage': len(nhtsa.get('analysis', {}).get('geographic_distribution', {})) if 'error' not in nhtsa else 0
                    },
                    'cohort_system': {
                        'status': 'available' if 'error' not in cohorts else 'unavailable',
                        'cohort_count': len(cohorts.get('cohorts', {})) if 'error' not in cohorts else 0
                    }
                },
                'business_metrics': {
                    'total_data_points': (
                        len(leads.get('leads', [])) +
                        weather.get('validation_results', {}).get('accuracy_assessment', {}).get('total_comparisons', 0) +
                        nhtsa.get('total_battery_complaints', 0) +
                        len(cohorts.get('cohorts', {}))
                    ) if all('error' not in data for data in [leads, weather, nhtsa, cohorts]) else 0,
                    'credibility_score': self._calculate_credibility_score(leads, weather, nhtsa, cohorts),
                    'market_readiness': self._assess_market_readiness(leads, weather, nhtsa, cohorts)
                },
                'generated_at': datetime.now().isoformat()
            }
            
            return intelligence
            
        except Exception as e:
            self.logger.error(f"Error generating combined intelligence: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_credibility_score(self, leads: Dict, weather: Dict, nhtsa: Dict, cohorts: Dict) -> float:
        """Calculate a credibility score based on data availability and quality"""
        score = 0.0
        
        # Lead database (25 points)
        if 'error' not in leads and len(leads.get('leads', [])) >= 1000:
            score += 25.0
        elif 'error' not in leads and len(leads.get('leads', [])) >= 100:
            score += 15.0
        elif 'error' not in leads:
            score += 5.0
        
        # Weather validation (25 points)
        if 'error' not in weather:
            accuracy = weather.get('validation_results', {}).get('accuracy_assessment', {}).get('overall_accuracy', '')
            if accuracy in ['EXCELLENT', 'VERY_GOOD']:
                score += 25.0
            elif accuracy == 'GOOD':
                score += 20.0
            elif accuracy == 'ACCEPTABLE':
                score += 10.0
            else:
                score += 5.0
        
        # NHTSA validation (25 points)
        if 'error' not in nhtsa and nhtsa.get('total_battery_complaints', 0) >= 10:
            score += 25.0
        elif 'error' not in nhtsa and nhtsa.get('total_battery_complaints', 0) >= 5:
            score += 15.0
        elif 'error' not in nhtsa:
            score += 5.0
        
        # Cohort system (25 points)
        if 'error' not in cohorts and len(cohorts.get('cohorts', {})) >= 4:
            score += 25.0
        elif 'error' not in cohorts:
            score += 15.0
        
        return round(score, 1)
    
    def _assess_market_readiness(self, leads: Dict, weather: Dict, nhtsa: Dict, cohorts: Dict) -> str:
        """Assess overall market readiness based on data quality"""
        credibility = self._calculate_credibility_score(leads, weather, nhtsa, cohorts)
        
        if credibility >= 90:
            return "ENTERPRISE_READY"
        elif credibility >= 70:
            return "MARKET_READY"
        elif credibility >= 50:
            return "PILOT_READY"
        else:
            return "DEVELOPMENT"
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self.data_cache.clear()
        self.cache_expiry.clear()
        self.logger.info("Cache cleared")
    
    def optimize_for_production(self) -> Dict:
        """Optimize system for production deployment"""
        optimization_results = {
            'timestamp': datetime.now().isoformat(),
            'optimizations_applied': [],
            'warnings': [],
            'recommendations': []
        }
        
        try:
            # Pre-load and cache all data
            self.load_lead_database()
            self.load_weather_validation()
            self.load_nhtsa_complaints()
            self.load_cohort_data()
            optimization_results['optimizations_applied'].append("Pre-loaded all data sources")
            
            # Check data file sizes for optimization
            file_checks = [
                ("vin_leads_database_*.json", "Lead database"),
                ("weather_validation_*.json", "Weather validation"),
                ("nhtsa_ford_complaints_*.json", "NHTSA complaints")
            ]
            
            for pattern, name in file_checks:
                latest_file = self.get_latest_file(pattern)
                if latest_file:
                    file_size = os.path.getsize(latest_file)
                    if file_size > 10 * 1024 * 1024:  # 10MB
                        optimization_results['warnings'].append(f"{name} file is large ({file_size // 1024 // 1024}MB)")
                        optimization_results['recommendations'].append(f"Consider compressing {name} data")
            
            # Validate integration health
            status = self.get_integration_status()
            if status['system_health']['active_integrations'] < status['system_health']['total_integrations']:
                optimization_results['warnings'].append("Some integrations are not active")
                optimization_results['recommendations'].append("Check failed integrations and repair data files")
            
            optimization_results['optimizations_applied'].append("Validated integration health")
            optimization_results['optimizations_applied'].append("Enabled caching with 6-hour expiry")
            optimization_results['optimizations_applied'].append("Optimized file access patterns")
            
            self.logger.info("Production optimization completed")
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Error during optimization: {str(e)}")
            optimization_results['warnings'].append(f"Optimization error: {str(e)}")
            return optimization_results

# Global integration manager instance
integration_manager = IntegrationManager() 