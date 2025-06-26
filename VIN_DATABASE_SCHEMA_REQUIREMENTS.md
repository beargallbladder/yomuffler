# VIN Stressors Lead Database Schema Requirements

## 🎯 **Objective**
Generate 5,000-10,000 realistic vehicle leads for **Southeast region** with:
- Light and midweight trucks (30,000-50,000 miles)  
- **2+ standard deviations** from Argonne National Laboratory studies
- Temperature delta-based stressor calculations
- Bayesian risk scoring using academic methodology

---

## 📋 **DATA SCHEMA REQUIREMENTS**

### 🚗 **VEHICLE IDENTIFICATION**
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `vin` | String(17) | Valid Ford VIN format | `1FTFW1ET5LFA67890` |
| `year` | Integer | 2020-2023 (1-4 years old) | `2022` |
| `make` | String | Vehicle manufacturer | `Ford` |
| `model` | String | F-150, F-250, F-350, Ranger, Explorer, Expedition | `F-150` |
| `vehicle_type` | String | light_truck, midweight_truck, suv | `light_truck` |
| `weight_class` | String | Classification for cohort assignment | `light` |
| `current_mileage` | Integer | 30,000-50,000 range | `47823` |
| `vehicle_age` | Integer | Years since manufacture | `2` |

### 📍 **GEOGRAPHIC DATA**
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `zip_code` | String(5) | Southeast ZIP codes only | `33101` |
| `city` | String | Major Southeast cities | `Miami` |
| `state` | String(2) | FL, GA, SC, NC, TN, AL, MS, LA | `FL` |
| `climate_zone` | String | coastal_hot, inland_hot, coastal_moderate, inland_moderate, mountain_cool | `coastal_hot` |
| `temp_winter` | Integer | December-February average (°F) | `68` |
| `temp_summer` | Integer | June-August average (°F) | `84` |
| `temperature_delta` | Integer | Summer high - Winter low | `16` |

### 🔥 **STRESSOR ANALYSIS (2+ Standard Deviations)**
| Field | Type | Description | Argonne Baseline |
|-------|------|-------------|------------------|
| `start_cycles_annual` | Integer | Annual ignition cycles | 1,200 baseline |
| `start_cycle_deviation` | Float | Multiplier vs baseline (2+ std dev) | `2.2-3.0` range |
| `temperature_stress` | Float | Climate stress multiplier | `0.0-0.5` |
| `short_trip_percentage` | Float | % trips under 6 miles (recharge rule) | `0.4-0.8` for high stress |
| `estimated_cold_starts` | Integer | Winter starting cycles | `30%` of annual starts |

### 🧮 **ARGONNE-BASED BAYESIAN CALCULATIONS**
| Field | Type | Description | ANL-115925.pdf Source |
|-------|------|-------------|----------------------|
| `base_prior` | Float | Vehicle type baseline failure rate | 15%, 12%, 9%, 18% by cohort |
| `adjusted_prior` | Float | Prior × environment × usage | Calculated field |
| `active_lrs` | Array | Active likelihood ratios | `[2.39, 2.16, 6.50, 1.9]` |
| `combined_lr` | Float | Product of active LRs | Calculated field |
| `posterior_probability` | Float | Final Bayesian result | P(Failure\|Evidence) |
| `risk_percentile` | Integer | Ranking within cohort (0-100) | Calculated field |
| `urgency_score` | Integer | Lead priority score (0-100) | Calculated field |

### 💰 **BUSINESS INTELLIGENCE**
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `primary_service` | String | Recommended action | `battery_replacement` |
| `parts_cost` | Integer | Parts pricing by vehicle | `$280` (F-150 battery) |
| `service_cost` | Integer | Labor and diagnostic | `$125` |
| `total_opportunity` | Integer | Parts + service revenue | `$405` |
| `contact_urgency` | String | immediate, 24_hours, 48_hours | `immediate` |
| `predicted_failure_window` | String | Estimated timeline | `2-6_weeks` |

### 👤 **CUSTOMER DATA**
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `lead_id` | Integer | Unique identifier | `1-10000` |
| `customer_name` | String | Realistic name generation | `Sarah Johnson` |
| `cohort_assignment` | String | Vehicle + climate classification | `light_truck_coastal_hot` |

---

## 🏗️ **DATA GENERATION STRATEGY**

### **1. Geographic Distribution**
**Southeast ZIP Codes with Climate Data:**
```
Florida: 33101 (Miami), 32801 (Orlando), 33602 (Tampa), 32501 (Pensacola)
Georgia: 30309 (Atlanta), 31401 (Savannah), 31201 (Macon)  
South Carolina: 29401 (Charleston), 29201 (Columbia)
North Carolina: 28202 (Charlotte), 27601 (Raleigh), 28801 (Asheville)
Tennessee: 37201 (Nashville), 38101 (Memphis)
Alabama: 35203 (Birmingham), 36104 (Montgomery)
Mississippi: 39201 (Jackson), 39501 (Gulfport)
Louisiana: 70112 (New Orleans), 70801 (Baton Rouge)
```

### **2. Vehicle Distribution Target**
- **60%** Light Trucks (F-150, Ranger)
- **25%** Midweight Trucks (F-250, F-350)  
- **15%** SUVs (Explorer, Expedition)

### **3. Stressor Criteria (2+ Standard Deviations)**
**High Stress Scenarios:**
- Annual mileage >15,000 → Start cycle multiplier 1.8-2.6x
- Annual mileage <8,000 → Start cycle multiplier 2.2-3.0x (short trips)
- Temperature delta >40°F → Additional climate stress
- Short trip percentage >50% → 6-mile recharge rule violations

### **4. Argonne Constants (ANL-115925.pdf)**
```python
LIKELIHOOD_RATIOS = {
    "temperature_cycling": 2.39,
    "ignition_frequency": 2.16, 
    "soc_decline": 6.50,
    "short_trips": 1.9
}

BASE_PRIORS = {
    "light_truck": 0.15,    # 15% baseline
    "midweight_truck": 0.18, # 18% baseline  
    "suv": 0.12             # 12% baseline
}
```

### **5. Revenue Calculations**
**Realistic Parts Pricing:**
- F-150 Battery: $280 + $125 service = $405
- F-250 Battery: $320 + $145 service = $465
- Explorer Battery: $260 + $110 service = $370

---

## 📊 **OUTPUT SPECIFICATIONS**

### **File Formats:**
1. **JSON**: Complete data with nested structures
2. **CSV**: Flat file for spreadsheet analysis  
3. **Summary Report**: Business intelligence overview

### **Database Size Options:**
- **5,000 leads**: Standard demo database
- **10,000 leads**: Enterprise-scale demonstration
- **Custom range**: Adjustable based on needs

### **Quality Targets:**
- **80%+ leads** with 2+ standard deviation stressors
- **Geographic distribution** across all Southeast states
- **Risk distribution**: 30% high-risk (60%+), 40% medium (30-60%), 30% low (<30%)
- **Revenue opportunity**: $200-500 average per lead

---

## 🚀 **EXECUTION COMMAND**

```bash
# Generate 5,000 leads
python3 scripts/generate_lead_database.py

# Or edit for 10,000 leads:
# Change num_leads = 10000 in main() function
```

**Generated Files:**
- `vin_leads_database_YYYYMMDD_HHMMSS.json`
- `vin_leads_database_YYYYMMDD_HHMMSS.csv` 
- `vin_leads_database_summary_YYYYMMDD_HHMMSS.txt`

---

## ✅ **VALIDATION CHECKLIST**

- [ ] All VINs follow Ford format standards
- [ ] Geographic distribution covers Southeast region
- [ ] Mileage within 30,000-50,000 range
- [ ] 2+ standard deviation stressor criteria met
- [ ] Bayesian calculations use Argonne methodology
- [ ] Revenue estimates based on realistic pricing
- [ ] Risk percentiles properly distributed
- [ ] Customer names appear realistic
- [ ] All required fields populated

**This schema creates enterprise-ready demo data that scales your 4-VIN demo to 5,000-10,000 realistic leads!** 🎯 