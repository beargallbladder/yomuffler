
// Enhanced Plausible Analytics Tracking for 100k VIN Analysis
// Automatically tracks user interactions with new features

// Regional Analysis Tracking
function trackRegionalAnalysis(region, vinCount, avgRevenue, capacityStatus) {
    if (window.plausible) {
        window.plausible('Regional Analysis Loaded', {
            props: {
                region: region,
                vin_count: vinCount,
                avg_revenue: avgRevenue,
                capacity_status: capacityStatus
            }
        });
    }
}

// Lead Volume Optimization Tracking
function trackLeadVolumeOptimization(region, utilization, optimizationType, reduction) {
    if (window.plausible) {
        window.plausible('Lead Volume Optimization', {
            props: {
                region: region,
                current_utilization: utilization + '%',
                optimization_type: optimizationType,
                expected_reduction: reduction
            }
        });
    }
}

// DTC Integration Analysis Tracking
function trackDTCIntegration(integrationRate, bundlingOps, revenueIncrease) {
    if (window.plausible) {
        window.plausible('DTC Integration Analysis', {
            props: {
                integration_rate: integrationRate + '%',
                bundling_opportunities: bundlingOps,
                revenue_increase: '$' + revenueIncrease
            }
        });
    }
}

// Customer Engagement Demo Tracking
function trackCustomerEngagement(scenarioType, strategy, revenue) {
    if (window.plausible) {
        window.plausible('Customer Engagement Demo', {
            props: {
                scenario_type: scenarioType,
                messaging_strategy: strategy,
                revenue_opportunity: '$' + revenue
            }
        });
    }
}

// Regional Strategy Optimization Tracking
function trackRegionalStrategy(bestRegion, worstRegion, gap, recommendation) {
    if (window.plausible) {
        window.plausible('Regional Strategy Optimization', {
            props: {
                best_region: bestRegion,
                worst_region: worstRegion,
                performance_gap: '$' + gap,
                optimization_recommendation: recommendation
            }
        });
    }
}

// Scaling Insights Analysis Tracking
function trackScalingInsights(totalVins, totalRevenue, avgPerVehicle, scalingFactor) {
    if (window.plausible) {
        window.plausible('Scaling Insights Analysis', {
            props: {
                total_vins: totalVins.toLocaleString(),
                total_revenue: '$' + totalRevenue.toLocaleString(),
                avg_per_vehicle: '$' + avgPerVehicle,
                scaling_factor: scalingFactor + 'x'
            }
        });
    }
}

// Revenue Opportunity Drill Down Tracking
function trackRevenueDrillDown(model, region, riskScore, bundlingType, revenue) {
    if (window.plausible) {
        window.plausible('Revenue Opportunity Drill Down', {
            props: {
                vehicle_model: model,
                region: region,
                risk_score: riskScore + '%',
                bundling_type: bundlingType,
                total_revenue: '$' + revenue
            }
        });
    }
}

// Cohort Performance Analysis Tracking
function trackCohortPerformance(cohortType, outlierPct, avgRisk, actionableLeads) {
    if (window.plausible) {
        window.plausible('Cohort Performance Analysis', {
            props: {
                cohort_type: cohortType,
                outlier_percentage: outlierPct + '%',
                avg_risk: avgRisk,
                actionable_leads: actionableLeads
            }
        });
    }
}

// Geographic Distribution Analysis Tracking
function trackGeographicAnalysis(regionCount, topRegion, strategy) {
    if (window.plausible) {
        window.plausible('Geographic Distribution Analysis', {
            props: {
                region_count: regionCount,
                highest_performing_region: topRegion,
                geographic_strategy: strategy
            }
        });
    }
}

// Capacity Management Planning Tracking
function trackCapacityPlanning(overCapacity, underCapacity, investment) {
    if (window.plausible) {
        window.plausible('Capacity Management Planning', {
            props: {
                over_capacity_regions: overCapacity,
                under_capacity_regions: underCapacity,
                investment_needed: '$' + investment
            }
        });
    }
}

// Stressor Framework Analysis Tracking
function trackStressorFramework(stressorCount, frameworkType, distribution, sources) {
    if (window.plausible) {
        window.plausible('Stressor Framework Analysis', {
            props: {
                stressor_count: stressorCount,
                framework_type: frameworkType,
                risk_distribution: distribution,
                academic_sources: sources
            }
        });
    }
}

// Predictive Model Performance Tracking
function trackModelPerformance(version, accuracy, confidence, validation) {
    if (window.plausible) {
        window.plausible('Predictive Model Performance', {
            props: {
                model_version: version,
                accuracy_rate: accuracy + '%',
                prediction_confidence: confidence + '%',
                academic_validation: validation
            }
        });
    }
}

// Business ROI Calculator Tracking
function trackROICalculation(scenario, roi, breakEven, riskReduction) {
    if (window.plausible) {
        window.plausible('Business ROI Calculator', {
            props: {
                investment_scenario: scenario,
                projected_roi: roi + '%',
                break_even_months: breakEven,
                risk_reduction: riskReduction + '%'
            }
        });
    }
}

// Auto-tracking for page interactions
document.addEventListener('DOMContentLoaded', function() {
    // Track when user interacts with 100k analysis features
    
    // Example: Auto-track regional performance interactions
    const regionalCards = document.querySelectorAll('.regional-performance-card');
    regionalCards.forEach(card => {
        card.addEventListener('click', function() {
            const region = this.dataset.region;
            const vinCount = this.dataset.vinCount;
            const avgRevenue = this.dataset.avgRevenue;
            const capacityStatus = this.dataset.capacityStatus;
            
            trackRegionalAnalysis(region, vinCount, avgRevenue, capacityStatus);
        });
    });
    
    // Example: Auto-track optimization tool usage
    const optimizationButtons = document.querySelectorAll('.optimization-button');
    optimizationButtons.forEach(button => {
        button.addEventListener('click', function() {
            const region = this.dataset.region;
            const utilization = this.dataset.utilization;
            const type = this.dataset.optimizationType;
            const reduction = this.dataset.expectedReduction;
            
            trackLeadVolumeOptimization(region, utilization, type, reduction);
        });
    });
});

// Console helper for manual tracking
console.log('🔍 Enhanced Plausible Analytics loaded!');
console.log('Use trackRegionalAnalysis(), trackLeadVolumeOptimization(), etc. for manual tracking');
