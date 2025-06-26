#!/usr/bin/env python3
"""
Real VIN Data Integration Guide for VIN Stressors Platform
Shows how to replace synthetic data with real customer data
"""

import json
import csv
import pandas as pd
from datetime import datetime
from pathlib import Path

class RealDataIntegrator:
    """Integrate real VIN data into the VIN Stressors system"""
    
    def __init__(self):
        self.required_fields = [
            'vin',                  # 17-character VIN (REQUIRED)
            'customer_name',        # Customer name (REQUIRED) 
            'current_mileage',      # Odometer reading (REQUIRED)
            'zip_code',            # 5-digit ZIP code (REQUIRED)
            'year',                # Vehicle year (can be decoded from VIN)
            'make',                # Vehicle make (can be decoded from VIN) 
            'model',               # Vehicle model (can be decoded from VIN)
            'city',                # City name (can be looked up from ZIP)
            'state'                # State code (can be looked up from ZIP)
        ]
        
        self.optional_fields = [
            'vehicle_age',          # Calculated if not provided
            'climate_zone',         # Looked up from ZIP code
            'temp_winter',          # From weather validation system
            'temp_summer',          # From weather validation system
            'temperature_delta'     # Calculated automatically
        ]
        
        self.calculated_fields = [
            'start_cycles_annual',      # Based on mileage and usage patterns
            'start_cycle_deviation',    # Statistical analysis vs baseline
            'temperature_stress',       # Climate impact calculation
            'short_trip_percentage',    # Estimated from mileage patterns
            'estimated_cold_starts',    # Winter driving calculation
            'base_prior',              # Vehicle type baseline risk
            'adjusted_prior',          # Environment-adjusted risk
            'active_lrs',             # Argonne likelihood ratios
            'combined_lr',            # Product of active LRs
            'posterior_probability',   # Bayesian risk score
            'risk_percentile',        # Ranking within cohort
            'urgency_score',          # Lead priority score
            'primary_service',        # Recommended action
            'parts_cost',             # Parts pricing
            'service_cost',           # Service pricing
            'total_opportunity',      # Revenue calculation
            'contact_urgency',        # Lead timing
            'cohort_assignment'       # Vehicle classification
        ]
    
    def validate_real_data(self, data_file: str) -> dict:
        """Validate real VIN data format and completeness"""
        
        validation_results = {
            'file_format': 'unknown',
            'total_records': 0,
            'valid_records': 0,
            'missing_fields': [],
            'validation_errors': [],
            'sample_record': None
        }
        
        try:
            # Detect file format
            if data_file.endswith('.csv'):
                validation_results['file_format'] = 'CSV'
                df = pd.read_csv(data_file)
            elif data_file.endswith('.json'):
                validation_results['file_format'] = 'JSON'
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        df = pd.DataFrame(data)
                    else:
                        df = pd.DataFrame([data])
            else:
                validation_results['validation_errors'].append("Unsupported file format")
                return validation_results
            
            validation_results['total_records'] = len(df)
            
            # Check required fields
            missing_fields = []
            for field in self.required_fields:
                if field not in df.columns:
                    missing_fields.append(field)
            
            validation_results['missing_fields'] = missing_fields
            
            # Validate individual records
            valid_count = 0
            for index, row in df.iterrows():
                is_valid = True
                
                # Check VIN format (17 characters, alphanumeric)
                vin = str(row.get('vin', ''))
                if len(vin) != 17 or not vin.isalnum():
                    is_valid = False
                    validation_results['validation_errors'].append(f"Invalid VIN at row {index}: {vin}")
                
                # Check mileage (positive integer)
                try:
                    mileage = int(row.get('current_mileage', 0))
                    if mileage <= 0 or mileage > 500000:
                        is_valid = False
                        validation_results['validation_errors'].append(f"Invalid mileage at row {index}: {mileage}")
                except (ValueError, TypeError):
                    is_valid = False
                    validation_results['validation_errors'].append(f"Non-numeric mileage at row {index}")
                
                # Check ZIP code (5 digits)
                zip_code = str(row.get('zip_code', ''))
                if not zip_code.isdigit() or len(zip_code) != 5:
                    is_valid = False
                    validation_results['validation_errors'].append(f"Invalid ZIP code at row {index}: {zip_code}")
                
                if is_valid:
                    valid_count += 1
                    if validation_results['sample_record'] is None:
                        validation_results['sample_record'] = row.to_dict()
            
            validation_results['valid_records'] = valid_count
            
        except Exception as e:
            validation_results['validation_errors'].append(f"File processing error: {str(e)}")
        
        return validation_results
    
    def create_sample_real_data_template(self, filename: str = "real_data_template.csv"):
        """Create a template for real VIN data input"""
        
        sample_data = [
            {
                'vin': '1FTFW1E43MKF12345',
                'customer_name': 'John Smith',
                'current_mileage': 45000,
                'zip_code': '33101',
                'year': 2022,
                'make': 'Ford',
                'model': 'F-150',
                'city': 'Miami',
                'state': 'FL'
            },
            {
                'vin': '1FTFW1E43MKF67890', 
                'customer_name': 'Sarah Johnson',
                'current_mileage': 62000,
                'zip_code': '30309',
                'year': 2021,
                'make': 'Ford', 
                'model': 'F-250',
                'city': 'Atlanta',
                'state': 'GA'
            },
            {
                'vin': '1FMCU0GD3HU123456',
                'customer_name': 'Mike Rodriguez',
                'current_mileage': 38000,
                'zip_code': '28202',
                'year': 2023,
                'make': 'Ford',
                'model': 'Explorer',
                'city': 'Charlotte', 
                'state': 'NC'
            }
        ]
        
        # Create CSV template
        df = pd.DataFrame(sample_data)
        df.to_csv(filename, index=False)
        
        # Create documentation
        doc_filename = filename.replace('.csv', '_documentation.txt')
        with open(doc_filename, 'w') as f:
            f.write("REAL VIN DATA TEMPLATE DOCUMENTATION\n")
            f.write("=" * 50 + "\n\n")
            f.write("REQUIRED FIELDS:\n")
            for field in self.required_fields:
                f.write(f"  ✅ {field}\n")
            f.write("\nOPTIONAL FIELDS (auto-calculated if missing):\n")
            for field in self.optional_fields:
                f.write(f"  🔄 {field}\n")
            f.write("\nCALCULATED FIELDS (automatic):\n")
            for field in self.calculated_fields:
                f.write(f"  🤖 {field}\n")
            
            f.write("\n\nDATA REQUIREMENTS:\n")
            f.write("  • VIN: 17-character alphanumeric Ford VIN\n")
            f.write("  • Mileage: 1-500,000 miles\n")
            f.write("  • ZIP Code: 5-digit US ZIP code\n")
            f.write("  • Customer Name: Any format\n")
            f.write("  • Year/Make/Model: Can be decoded from VIN if missing\n")
        
        print(f"📄 Real data template created: {filename}")
        print(f"📋 Documentation: {doc_filename}")
        return filename, doc_filename
    
    def integration_workflow(self):
        """Show the complete workflow for real data integration"""
        
        workflow = {
            'step_1_data_preparation': {
                'description': 'Prepare your real VIN data',
                'actions': [
                    'Export customer data with VINs and mileage',
                    'Clean data (remove duplicates, invalid VINs)',
                    'Format as CSV or JSON following template',
                    'Validate ZIP codes and mileage values'
                ],
                'tools': ['Excel/CSV export', 'Data validation script']
            },
            'step_2_system_integration': {
                'description': 'Integrate with VIN Stressors platform',
                'actions': [
                    'Run validation script on real data',
                    'Replace synthetic database file',
                    'Restart integration manager',
                    'Verify all calculations work'
                ],
                'tools': ['validation script', 'integration manager']
            },
            'step_3_business_deployment': {
                'description': 'Deploy for business use',
                'actions': [
                    'Test with sample real VINs',
                    'Verify risk calculations',
                    'Train team on new data',
                    'Monitor system performance'
                ],
                'tools': ['Risk calculation API', 'Dealer portal']
            }
        }
        
        return workflow
    
    def show_data_comparison(self):
        """Show the difference between synthetic and real data"""
        
        print("📊 SYNTHETIC vs REAL DATA COMPARISON")
        print("=" * 50)
        
        comparison = {
            'synthetic_data': {
                'pros': [
                    '✅ Scientifically generated using Argonne research',
                    '✅ Controlled stressor distribution (2+ std dev)',
                    '✅ Perfect geographic coverage',
                    '✅ No privacy concerns',
                    '✅ Ideal for demos and testing'
                ],
                'cons': [
                    '❌ Not actual customers',
                    '❌ Limited business impact validation',
                    '❌ May not reflect real usage patterns'
                ]
            },
            'real_data': {
                'pros': [
                    '✅ Actual customer vehicles and usage',
                    '✅ Real business revenue opportunity',
                    '✅ Authentic stressor patterns',
                    '✅ Direct customer contact capability',
                    '✅ Measurable ROI from interventions'
                ],
                'cons': [
                    '❌ Requires customer data access',
                    '❌ Privacy and compliance considerations',
                    '❌ May have data quality issues',
                    '❌ Geographic distribution may be uneven'
                ]
            }
        }
        
        for data_type, details in comparison.items():
            print(f"\n{data_type.upper().replace('_', ' ')}:")
            print("PROS:")
            for pro in details['pros']:
                print(f"  {pro}")
            print("CONS:")
            for con in details['cons']:
                print(f"  {con}")
        
        return comparison

def main():
    """Demonstrate real data integration capabilities"""
    
    print("🚀 REAL VIN DATA INTEGRATION GUIDE")
    print("=" * 50)
    print("Your VIN Stressors system is ready for real customer data!\n")
    
    integrator = RealDataIntegrator()
    
    # Create template
    template_file, doc_file = integrator.create_sample_real_data_template()
    
    # Show workflow
    workflow = integrator.integration_workflow()
    print(f"\n📋 INTEGRATION WORKFLOW:")
    for step, details in workflow.items():
        step_num = step.split('_')[1]
        print(f"\nSTEP {step_num}: {details['description']}")
        for action in details['actions']:
            print(f"  • {action}")
    
    # Show comparison
    integrator.show_data_comparison()
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. 📄 Use the template file to format your real VIN data")
    print("2. 🔍 Run validation on your data file")  
    print("3. 🔄 Replace synthetic data with real data")
    print("4. 🚀 Your system works exactly the same with real data!")
    
    print(f"\n✨ The system calculates ALL stressor analysis automatically!")
    print("You just provide: VIN + Mileage + Location = Full Risk Analysis")

if __name__ == "__main__":
    main() 