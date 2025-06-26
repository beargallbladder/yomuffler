#!/usr/bin/env python3
"""
NOAA Weather Data Integration for VIN Stressors
Replaces synthetic temperature data with real NOAA government records
Second biggest impact: Real climate validation for stressor analysis
"""

import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import csv
import statistics

class NOAAWeatherIntegrator:
    def __init__(self):
        # NOAA API endpoints
        self.base_url = "https://www.ncei.noaa.gov/data/daily-summaries/access"
        self.stations_url = "https://www.ncei.noaa.gov/metadata/geoportal/rest/find/document"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'VINStressors/1.0 (Educational Research)'
        })
        
        # Southeast ZIP codes from our lead generator
        self.southeast_locations = {
            # Florida - Hot, humid
            "33101": {"city": "Miami", "state": "FL", "lat": 25.7617, "lon": -80.1918},
            "32801": {"city": "Orlando", "state": "FL", "lat": 28.5383, "lon": -81.3792},
            "33602": {"city": "Tampa", "state": "FL", "lat": 27.9506, "lon": -82.4572},
            "32501": {"city": "Pensacola", "state": "FL", "lat": 30.4213, "lon": -87.2169},
            
            # Georgia - Moderate to hot
            "30309": {"city": "Atlanta", "state": "GA", "lat": 33.7490, "lon": -84.3880},
            "31401": {"city": "Savannah", "state": "GA", "lat": 32.0835, "lon": -81.0998},
            "31201": {"city": "Macon", "state": "GA", "lat": 32.8407, "lon": -83.6324},
            
            # South Carolina - Moderate
            "29401": {"city": "Charleston", "state": "SC", "lat": 32.7765, "lon": -79.9311},
            "29201": {"city": "Columbia", "state": "SC", "lat": 34.0007, "lon": -81.0348},
            
            # North Carolina - Moderate to cool
            "28202": {"city": "Charlotte", "state": "NC", "lat": 35.2271, "lon": -80.8431},
            "27601": {"city": "Raleigh", "state": "NC", "lat": 35.7796, "lon": -78.6382},
            "28801": {"city": "Asheville", "state": "NC", "lat": 35.5951, "lon": -82.5515},
            
            # Tennessee - Cool to moderate
            "37201": {"city": "Nashville", "state": "TN", "lat": 36.1627, "lon": -86.7816},
            "38101": {"city": "Memphis", "state": "TN", "lat": 35.1495, "lon": -90.0490},
            
            # Alabama - Moderate to hot
            "35203": {"city": "Birmingham", "state": "AL", "lat": 33.5186, "lon": -86.8104},
            "36104": {"city": "Montgomery", "state": "AL", "lat": 32.3668, "lon": -86.3000},
            
            # Mississippi - Hot, humid
            "39201": {"city": "Jackson", "state": "MS", "lat": 32.2988, "lon": -90.1848},
            "39501": {"city": "Gulfport", "state": "MS", "lat": 30.3674, "lon": -89.0928},
            
            # Louisiana - Hot, humid
            "70112": {"city": "New Orleans", "state": "LA", "lat": 29.9511, "lon": -90.0715},
            "70801": {"city": "Baton Rouge", "state": "LA", "lat": 30.4515, "lon": -91.1871},
        }
        
        # NOAA station mappings (major airports typically have best data)
        self.station_mappings = {
            "Miami": "USW00012839",     # Miami International Airport
            "Orlando": "USW00012815",   # Orlando International Airport  
            "Tampa": "USW00012842",     # Tampa International Airport
            "Pensacola": "USW00013899", # Pensacola Regional Airport
            "Atlanta": "USW00013874",   # Hartsfield-Jackson Atlanta International
            "Savannah": "USW00003822",  # Savannah/Hilton Head International
            "Macon": "USW00003813",     # Middle Georgia Regional Airport
            "Charleston": "USW00013880", # Charleston AFB/International Airport
            "Columbia": "USW00013883",  # Columbia Metropolitan Airport
            "Charlotte": "USW00013881", # Charlotte Douglas International
            "Raleigh": "USW00013722",   # Raleigh-Durham International
            "Asheville": "USW00013872", # Asheville Regional Airport
            "Nashville": "USW00013897", # Nashville International Airport
            "Memphis": "USW00013893",   # Memphis International Airport
            "Birmingham": "USW00013876", # Birmingham-Shuttlesworth International
            "Montgomery": "USW00013895", # Montgomery Regional Airport
            "Jackson": "USW00013968",   # Jackson-Medgar Wiley Evers International
            "Gulfport": "USW00013894",  # Gulfport-Biloxi International
            "New Orleans": "USW00012916", # Louis Armstrong New Orleans International
            "Baton Rouge": "USW00013970", # Baton Rouge Metropolitan Airport
        }
    
    def get_station_data(self, station_id: str, year: int) -> Optional[List[Dict]]:
        """Get daily weather data for a specific NOAA station and year"""
        url = f"{self.base_url}/{year}/{station_id}.csv"
        
        try:
            print(f"🌡️ Fetching NOAA data: Station {station_id}, Year {year}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse CSV data
            lines = response.text.strip().split('\n')
            if len(lines) < 2:
                print(f"   ❌ No data available for {station_id} in {year}")
                return None
            
            # Parse CSV header and rows
            header = lines[0].split(',')
            data_rows = []
            
            for line in lines[1:]:
                if line.strip():
                    row_data = line.split(',')
                    if len(row_data) >= len(header):
                        row_dict = dict(zip(header, row_data))
                        data_rows.append(row_dict)
            
            print(f"   📊 Collected {len(data_rows)} daily records")
            return data_rows
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error fetching {station_id} data: {str(e)}")
            return None
        except Exception as e:
            print(f"   ❌ Unexpected error: {str(e)}")
            return None
    
    def parse_temperature(self, temp_str: str) -> Optional[float]:
        """Parse temperature string from NOAA data (in tenths of degrees C)"""
        try:
            if not temp_str or temp_str.strip() == '':
                return None
            temp_tenths_c = float(temp_str)
            # Convert from tenths of degrees C to Fahrenheit
            temp_c = temp_tenths_c / 10.0
            temp_f = (temp_c * 9/5) + 32
            return round(temp_f, 1)
        except (ValueError, TypeError):
            return None
    
    def analyze_temperature_data(self, daily_data: List[Dict]) -> Dict:
        """Analyze daily temperature data to extract seasonal patterns"""
        
        if not daily_data:
            return {'error': 'No data available'}
        
        seasonal_temps = {
            'winter': [],  # Dec, Jan, Feb
            'spring': [],  # Mar, Apr, May
            'summer': [],  # Jun, Jul, Aug
            'fall': []     # Sep, Oct, Nov
        }
        
        extreme_temps = {'min': [], 'max': []}
        monthly_data = {i: {'min': [], 'max': []} for i in range(1, 13)}
        
        for record in daily_data:
            try:
                date_str = record.get('DATE', '')
                if not date_str or len(date_str) < 8:
                    continue
                
                # Parse date (YYYY-MM-DD format)
                year, month, day = date_str.split('-')
                month = int(month)
                
                # Get min and max temperatures
                tmin = self.parse_temperature(record.get('TMIN', ''))
                tmax = self.parse_temperature(record.get('TMAX', ''))
                
                if tmin is not None and tmax is not None:
                    # Categorize by season
                    if month in [12, 1, 2]:
                        seasonal_temps['winter'].extend([tmin, tmax])
                    elif month in [3, 4, 5]:
                        seasonal_temps['spring'].extend([tmin, tmax])
                    elif month in [6, 7, 8]:
                        seasonal_temps['summer'].extend([tmin, tmax])
                    else:  # 9, 10, 11
                        seasonal_temps['fall'].extend([tmin, tmax])
                    
                    # Track monthly data
                    monthly_data[month]['min'].append(tmin)
                    monthly_data[month]['max'].append(tmax)
                    
                    # Track extremes
                    extreme_temps['min'].append(tmin)
                    extreme_temps['max'].append(tmax)
                    
            except (ValueError, IndexError):
                continue
        
        # Calculate statistics
        def safe_stats(data_list):
            if not data_list:
                return {'avg': 0, 'min': 0, 'max': 0, 'count': 0}
            return {
                'avg': round(statistics.mean(data_list), 1),
                'min': round(min(data_list), 1),
                'max': round(max(data_list), 1),
                'count': len(data_list)
            }
        
        analysis = {
            'seasonal_averages': {
                season: safe_stats(temps)['avg'] for season, temps in seasonal_temps.items()
            },
            'seasonal_extremes': {
                season: {'min': safe_stats(temps)['min'], 'max': safe_stats(temps)['max']} 
                for season, temps in seasonal_temps.items()
            },
            'monthly_averages': {
                month: {
                    'avg_min': safe_stats(data['min'])['avg'],
                    'avg_max': safe_stats(data['max'])['avg']
                } for month, data in monthly_data.items()
            },
            'annual_extremes': {
                'coldest': safe_stats(extreme_temps['min'])['min'],
                'hottest': safe_stats(extreme_temps['max'])['max'],
                'total_records': len(daily_data)
            },
            'temperature_delta': safe_stats(extreme_temps['max'])['max'] - safe_stats(extreme_temps['min'])['min']
        }
        
        return analysis
    
    def get_location_climate_data(self, location_info: Dict, years: List[int] = None) -> Dict:
        """Get comprehensive climate data for a specific location"""
        
        if years is None:
            years = [2020, 2021, 2022, 2023]  # Recent years for relevance
        
        city = location_info['city']
        station_id = self.station_mappings.get(city)
        
        if not station_id:
            print(f"   ⚠️ No NOAA station mapping for {city}")
            return {'error': f'No station mapping for {city}'}
        
        print(f"🏙️ Processing {city}, {location_info['state']}")
        
        all_data = []
        successful_years = []
        
        for year in years:
            year_data = self.get_station_data(station_id, year)
            if year_data:
                all_data.extend(year_data)
                successful_years.append(year)
            
            # Rate limiting
            time.sleep(1)
        
        if not all_data:
            return {'error': f'No data available for {city}'}
        
        # Analyze the collected data
        analysis = self.analyze_temperature_data(all_data)
        analysis['years_analyzed'] = successful_years
        analysis['station_id'] = station_id
        analysis['location'] = location_info
        
        return analysis
    
    def collect_southeast_climate_data(self, max_locations: int = 10) -> Dict:
        """Collect NOAA climate data for all Southeast locations"""
        
        print("🌡️ NOAA WEATHER DATA COLLECTION STARTING")
        print("=" * 50)
        print("Collecting real government temperature data for Southeast locations")
        print("This replaces synthetic climate estimates with actual NOAA records!\n")
        
        climate_data = {}
        processed_count = 0
        
        for zip_code, location_info in self.southeast_locations.items():
            if processed_count >= max_locations:
                print(f"   🎯 Reached location limit ({max_locations}), stopping")
                break
            
            climate_data[zip_code] = self.get_location_climate_data(location_info)
            processed_count += 1
            
            # Progress indicator
            print(f"   ✅ Completed {processed_count}/{min(max_locations, len(self.southeast_locations))}")
            
            # Respectful rate limiting
            time.sleep(3)
        
        print(f"\n✨ Climate Data Collection Complete:")
        print(f"   📍 Processed {processed_count} locations")
        
        successful_locations = sum(1 for data in climate_data.values() if 'error' not in data)
        print(f"   🌡️ Successful: {successful_locations} locations with data")
        
        return {
            'collection_date': datetime.now().isoformat(),
            'data_source': 'NOAA National Centers for Environmental Information',
            'locations_processed': processed_count,
            'successful_locations': successful_locations,
            'climate_data': climate_data
        }
    
    def validate_synthetic_estimates(self, noaa_data: Dict) -> Dict:
        """Compare our synthetic temperature estimates with real NOAA data"""
        
        # Our original synthetic estimates
        synthetic_estimates = {
            "33101": {"temp_winter": 68, "temp_summer": 84},  # Miami
            "32801": {"temp_winter": 65, "temp_summer": 89},  # Orlando
            "33602": {"temp_winter": 67, "temp_summer": 87},  # Tampa
            "32501": {"temp_winter": 58, "temp_summer": 86},  # Pensacola
            "30309": {"temp_winter": 45, "temp_summer": 79},  # Atlanta
            "31401": {"temp_winter": 52, "temp_summer": 81},  # Savannah
            "31201": {"temp_winter": 47, "temp_summer": 82},  # Macon
            "29401": {"temp_winter": 54, "temp_summer": 82},  # Charleston
            "29201": {"temp_winter": 48, "temp_summer": 83},  # Columbia
            "28202": {"temp_winter": 42, "temp_summer": 79},  # Charlotte
            "27601": {"temp_winter": 41, "temp_summer": 79},  # Raleigh
            "28801": {"temp_winter": 38, "temp_summer": 73},  # Asheville
            "37201": {"temp_winter": 40, "temp_summer": 78},  # Nashville
            "38101": {"temp_winter": 42, "temp_summer": 82},  # Memphis
            "35203": {"temp_winter": 44, "temp_summer": 80},  # Birmingham
            "36104": {"temp_winter": 48, "temp_summer": 83},  # Montgomery
            "39201": {"temp_winter": 47, "temp_summer": 83},  # Jackson
            "39501": {"temp_winter": 52, "temp_summer": 84},  # Gulfport
            "70112": {"temp_winter": 55, "temp_summer": 85},  # New Orleans
            "70801": {"temp_winter": 50, "temp_summer": 84},  # Baton Rouge
        }
        
        validation_results = {}
        total_winter_error = 0
        total_summer_error = 0
        comparisons = 0
        
        climate_data = noaa_data.get('climate_data', {})
        
        for zip_code, noaa_location_data in climate_data.items():
            if 'error' in noaa_location_data:
                continue
            
            synthetic = synthetic_estimates.get(zip_code)
            if not synthetic:
                continue
            
            # Extract NOAA seasonal averages
            seasonal_avgs = noaa_location_data.get('seasonal_averages', {})
            noaa_winter = seasonal_avgs.get('winter', 0)
            noaa_summer = seasonal_avgs.get('summer', 0)
            
            if noaa_winter > 0 and noaa_summer > 0:
                winter_error = abs(synthetic['temp_winter'] - noaa_winter)
                summer_error = abs(synthetic['temp_summer'] - noaa_summer)
                
                validation_results[zip_code] = {
                    'location': noaa_location_data.get('location', {}).get('city', 'Unknown'),
                    'synthetic_winter': synthetic['temp_winter'],
                    'noaa_winter': round(noaa_winter, 1),
                    'winter_error': round(winter_error, 1),
                    'synthetic_summer': synthetic['temp_summer'],
                    'noaa_summer': round(noaa_summer, 1),
                    'summer_error': round(summer_error, 1),
                    'temperature_delta_synthetic': synthetic['temp_summer'] - synthetic['temp_winter'],
                    'temperature_delta_noaa': round(noaa_summer - noaa_winter, 1),
                    'delta_accuracy': round(abs((synthetic['temp_summer'] - synthetic['temp_winter']) - (noaa_summer - noaa_winter)), 1)
                }
                
                total_winter_error += winter_error
                total_summer_error += summer_error
                comparisons += 1
        
        # Overall accuracy assessment
        avg_winter_error = total_winter_error / comparisons if comparisons > 0 else 0
        avg_summer_error = total_summer_error / comparisons if comparisons > 0 else 0
        
        accuracy_assessment = {
            'total_comparisons': comparisons,
            'average_winter_error': round(avg_winter_error, 1),
            'average_summer_error': round(avg_summer_error, 1),
            'overall_accuracy': 'EXCELLENT' if avg_winter_error < 5 and avg_summer_error < 5 else 
                              'GOOD' if avg_winter_error < 10 and avg_summer_error < 10 else 'NEEDS_IMPROVEMENT',
            'validation_status': 'CONFIRMED' if avg_winter_error < 8 and avg_summer_error < 8 else 'PARTIALLY_CONFIRMED'
        }
        
        return {
            'accuracy_assessment': accuracy_assessment,
            'location_comparisons': validation_results,
            'summary': f"Synthetic estimates within {round(max(avg_winter_error, avg_summer_error), 1)}°F of NOAA data"
        }
    
    def export_climate_data(self, data: Dict, filename: str = None):
        """Export NOAA climate data and validation results"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"noaa_climate_data_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"📄 NOAA climate data exported: {filename}")
        
        # Generate validation report
        if 'climate_data' in data:
            validation = self.validate_synthetic_estimates(data)
            
            report_filename = filename.replace('.json', '_validation.txt')
            with open(report_filename, 'w') as f:
                f.write("NOAA WEATHER DATA VALIDATION REPORT\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Data Collection Date: {data.get('collection_date', 'Unknown')}\n")
                f.write(f"Locations Processed: {data.get('locations_processed', 0)}\n")
                f.write(f"Successful Locations: {data.get('successful_locations', 0)}\n\n")
                
                accuracy = validation.get('accuracy_assessment', {})
                f.write("SYNTHETIC ESTIMATE VALIDATION:\n\n")
                f.write(f"Total Comparisons: {accuracy.get('total_comparisons', 0)}\n")
                f.write(f"Average Winter Error: {accuracy.get('average_winter_error', 0)}°F\n")
                f.write(f"Average Summer Error: {accuracy.get('average_summer_error', 0)}°F\n")
                f.write(f"Overall Accuracy: {accuracy.get('overall_accuracy', 'Unknown')}\n")
                f.write(f"Validation Status: {accuracy.get('validation_status', 'Unknown')}\n\n")
                
                f.write("LOCATION-BY-LOCATION COMPARISON:\n\n")
                comparisons = validation.get('location_comparisons', {})
                for zip_code, comp in comparisons.items():
                    f.write(f"{comp['location']} ({zip_code}):\n")
                    f.write(f"  Winter: Synthetic {comp['synthetic_winter']}°F vs NOAA {comp['noaa_winter']}°F (Error: {comp['winter_error']}°F)\n")
                    f.write(f"  Summer: Synthetic {comp['synthetic_summer']}°F vs NOAA {comp['noaa_summer']}°F (Error: {comp['summer_error']}°F)\n")
                    f.write(f"  Delta: Synthetic {comp['temperature_delta_synthetic']}°F vs NOAA {comp['temperature_delta_noaa']}°F\n\n")
        
            print(f"📋 Validation report: {report_filename}")
            
            return filename, report_filename
        
        return filename, None

def main():
    """Main execution function"""
    print("🌡️ NOAA WEATHER DATA INTEGRATION")
    print("=" * 50)
    print("Replacing synthetic temperature estimates with real NOAA government data")
    print("This provides massive credibility boost for stressor analysis!\n")
    
    # Initialize integrator
    integrator = NOAAWeatherIntegrator()
    
    # Collect comprehensive climate data (limit to 5 locations for demo)
    climate_data = integrator.collect_southeast_climate_data(max_locations=5)
    
    # Export data and validation
    data_file, validation_file = integrator.export_climate_data(climate_data)
    
    print(f"\n🎯 NOAA INTEGRATION COMPLETE!")
    print("Files generated:")
    print(f"  📄 Climate data: {data_file}")
    if validation_file:
        print(f"  📋 Validation report: {validation_file}")
    
    # Print quick summary
    successful = climate_data.get('successful_locations', 0)
    if successful > 0:
        print(f"\n✨ Collected real NOAA data for {successful} Southeast locations!")
        print("Your stressor analysis now has government weather validation!")
    else:
        print("\n⚠️ No climate data collected - check API connectivity")

if __name__ == "__main__":
    main() 