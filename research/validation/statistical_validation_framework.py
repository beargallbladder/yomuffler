"""
Statistical Validation Framework for New Battery Stressors
Rigorous statistical testing to ensure new stressors improve prediction accuracy
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy.stats import pearsonr, spearmanr, chi2_contingency
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import roc_auc_score, precision_recall_curve, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Results of statistical validation for a potential stressor"""
    stressor_name: str
    correlation_coefficient: float
    p_value: float
    effect_size: float
    confidence_interval: Tuple[float, float]
    statistical_significance: bool
    practical_significance: bool
    validation_method: str
    sample_size: int
    power_analysis: Dict
    recommendation: str


@dataclass
class BacktestResult:
    """Results of backtesting with new stressor"""
    stressor_name: str
    baseline_accuracy: float
    enhanced_accuracy: float
    accuracy_improvement: float
    baseline_precision: float
    enhanced_precision: float
    precision_improvement: float
    baseline_recall: float
    enhanced_recall: float
    recall_improvement: float
    roc_auc_improvement: float
    false_positive_reduction: float
    business_impact_estimate: float
    statistical_significance: bool


class StatisticalValidationFramework:
    """
    Comprehensive framework for validating new battery stressors
    using rigorous statistical methods
    """
    
    def __init__(self, significance_level: float = 0.01, min_effect_size: float = 0.1):
        self.significance_level = significance_level
        self.min_effect_size = min_effect_size
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Statistical test configurations
        self.test_configs = {
            "correlation_tests": {
                "continuous_vs_continuous": "pearson",
                "ordinal_vs_continuous": "spearman", 
                "categorical_vs_continuous": "anova",
                "categorical_vs_categorical": "chi_square"
            },
            "effect_size_measures": {
                "pearson": "r_squared",
                "spearman": "rho_squared",
                "anova": "eta_squared",
                "chi_square": "cramers_v"
            }
        }
    
    def validate_correlation(self, 
                           stressor_data: np.ndarray, 
                           failure_data: np.ndarray,
                           stressor_name: str,
                           data_type: str = "continuous") -> ValidationResult:
        """
        Validate correlation between a potential stressor and battery failure
        
        Args:
            stressor_data: Array of stressor values
            failure_data: Binary array of failure outcomes
            stressor_name: Name of the stressor being tested
            data_type: Type of stressor data (continuous, ordinal, categorical)
        """
        
        # Remove any NaN values
        valid_mask = ~(np.isnan(stressor_data) | np.isnan(failure_data))
        stressor_clean = stressor_data[valid_mask]
        failure_clean = failure_data[valid_mask]
        
        sample_size = len(stressor_clean)
        
        if sample_size < 100:
            self.logger.warning(f"Small sample size ({sample_size}) for {stressor_name}")
        
        # Select appropriate correlation test
        if data_type == "continuous":
            # Pearson correlation for continuous data
            correlation_coef, p_value = pearsonr(stressor_clean, failure_clean)
            effect_size = correlation_coef ** 2  # R-squared
            validation_method = "pearson_correlation"
            
        elif data_type == "ordinal":
            # Spearman correlation for ordinal data
            correlation_coef, p_value = spearmanr(stressor_clean, failure_clean)
            effect_size = correlation_coef ** 2  # Rho-squared
            validation_method = "spearman_correlation"
            
        elif data_type == "categorical":
            # Chi-square test for categorical data
            contingency_table = pd.crosstab(stressor_clean, failure_clean)
            chi2, p_value, dof, expected = chi2_contingency(contingency_table)
            
            # Cramér's V as effect size
            n = contingency_table.sum().sum()
            correlation_coef = np.sqrt(chi2 / (n * (min(contingency_table.shape) - 1)))
            effect_size = correlation_coef
            validation_method = "chi_square_test"
        
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        # Calculate confidence interval (for continuous/ordinal)
        if data_type in ["continuous", "ordinal"]:
            confidence_interval = self._calculate_correlation_ci(
                correlation_coef, sample_size, confidence_level=1-self.significance_level
            )
        else:
            confidence_interval = (0.0, 1.0)  # Placeholder for categorical
        
        # Power analysis
        power_analysis = self._calculate_statistical_power(
            effect_size, sample_size, self.significance_level
        )
        
        # Determine significance
        statistical_significance = p_value < self.significance_level
        practical_significance = abs(effect_size) >= self.min_effect_size
        
        # Generate recommendation
        if statistical_significance and practical_significance:
            recommendation = "ACCEPT: Statistically and practically significant"
        elif statistical_significance and not practical_significance:
            recommendation = "CONDITIONAL: Statistically significant but small effect"
        elif not statistical_significance and practical_significance:
            recommendation = "INSUFFICIENT_DATA: Large effect but not statistically significant"
        else:
            recommendation = "REJECT: Neither statistically nor practically significant"
        
        return ValidationResult(
            stressor_name=stressor_name,
            correlation_coefficient=correlation_coef,
            p_value=p_value,
            effect_size=effect_size,
            confidence_interval=confidence_interval,
            statistical_significance=statistical_significance,
            practical_significance=practical_significance,
            validation_method=validation_method,
            sample_size=sample_size,
            power_analysis=power_analysis,
            recommendation=recommendation
        )
    
    def backtest_stressor_improvement(self,
                                    historical_data: pd.DataFrame,
                                    new_stressor_column: str,
                                    failure_column: str,
                                    baseline_features: List[str],
                                    test_periods: int = 5) -> BacktestResult:
        """
        Backtest prediction improvement with new stressor
        
        Args:
            historical_data: DataFrame with historical failure data
            new_stressor_column: Column name of new stressor to test
            failure_column: Column name of failure outcomes
            baseline_features: List of existing feature columns
            test_periods: Number of time-series cross-validation folds
        """
        
        # Prepare data
        X_baseline = historical_data[baseline_features].fillna(0)
        X_enhanced = historical_data[baseline_features + [new_stressor_column]].fillna(0)
        y = historical_data[failure_column]
        
        # Scale features
        scaler_baseline = StandardScaler()
        scaler_enhanced = StandardScaler()
        
        X_baseline_scaled = scaler_baseline.fit_transform(X_baseline)
        X_enhanced_scaled = scaler_enhanced.fit_transform(X_enhanced)
        
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=test_periods)
        
        # Models
        baseline_model = RandomForestClassifier(n_estimators=100, random_state=42)
        enhanced_model = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Collect results across folds
        baseline_accuracies = []
        enhanced_accuracies = []
        baseline_precisions = []
        enhanced_precisions = []
        baseline_recalls = []
        enhanced_recalls = []
        baseline_aucs = []
        enhanced_aucs = []
        fp_reductions = []
        
        for train_idx, test_idx in tscv.split(X_baseline_scaled):
            # Split data
            X_train_base, X_test_base = X_baseline_scaled[train_idx], X_baseline_scaled[test_idx]
            X_train_enh, X_test_enh = X_enhanced_scaled[train_idx], X_enhanced_scaled[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            # Fit models
            baseline_model.fit(X_train_base, y_train)
            enhanced_model.fit(X_train_enh, y_train)
            
            # Predictions
            y_pred_base = baseline_model.predict(X_test_base)
            y_pred_enh = enhanced_model.predict(X_test_enh)
            
            y_proba_base = baseline_model.predict_proba(X_test_base)[:, 1]
            y_proba_enh = enhanced_model.predict_proba(X_test_enh)[:, 1]
            
            # Calculate metrics
            from sklearn.metrics import accuracy_score, precision_score, recall_score
            
            baseline_accuracy = accuracy_score(y_test, y_pred_base)
            enhanced_accuracy = accuracy_score(y_test, y_pred_enh)
            
            baseline_precision = precision_score(y_test, y_pred_base, zero_division=0)
            enhanced_precision = precision_score(y_test, y_pred_enh, zero_division=0)
            
            baseline_recall = recall_score(y_test, y_pred_base, zero_division=0)
            enhanced_recall = recall_score(y_test, y_pred_enh, zero_division=0)
            
            baseline_auc = roc_auc_score(y_test, y_proba_base)
            enhanced_auc = roc_auc_score(y_test, y_proba_enh)
            
            # False positive reduction
            cm_base = confusion_matrix(y_test, y_pred_base)
            cm_enh = confusion_matrix(y_test, y_pred_enh)
            
            fp_base = cm_base[0, 1] if cm_base.shape == (2, 2) else 0
            fp_enh = cm_enh[0, 1] if cm_enh.shape == (2, 2) else 0
            
            fp_reduction = (fp_base - fp_enh) / max(fp_base, 1)
            
            # Store results
            baseline_accuracies.append(baseline_accuracy)
            enhanced_accuracies.append(enhanced_accuracy)
            baseline_precisions.append(baseline_precision)
            enhanced_precisions.append(enhanced_precision)
            baseline_recalls.append(baseline_recall)
            enhanced_recalls.append(enhanced_recall)
            baseline_aucs.append(baseline_auc)
            enhanced_aucs.append(enhanced_auc)
            fp_reductions.append(fp_reduction)
        
        # Calculate average improvements
        avg_baseline_accuracy = np.mean(baseline_accuracies)
        avg_enhanced_accuracy = np.mean(enhanced_accuracies)
        accuracy_improvement = avg_enhanced_accuracy - avg_baseline_accuracy
        
        avg_baseline_precision = np.mean(baseline_precisions)
        avg_enhanced_precision = np.mean(enhanced_precisions)
        precision_improvement = avg_enhanced_precision - avg_baseline_precision
        
        avg_baseline_recall = np.mean(baseline_recalls)
        avg_enhanced_recall = np.mean(enhanced_recalls)
        recall_improvement = avg_enhanced_recall - avg_baseline_recall
        
        avg_baseline_auc = np.mean(baseline_aucs)
        avg_enhanced_auc = np.mean(enhanced_aucs)
        roc_auc_improvement = avg_enhanced_auc - avg_baseline_auc
        
        avg_fp_reduction = np.mean(fp_reductions)
        
        # Statistical significance test for improvement
        accuracy_improvement_significance = stats.ttest_rel(
            enhanced_accuracies, baseline_accuracies
        ).pvalue < self.significance_level
        
        # Business impact estimate (simplified)
        # Assume $1000 per false positive reduced and $2000 per true positive gained
        total_predictions = len(y)
        fp_cost_savings = avg_fp_reduction * total_predictions * 1000
        tp_revenue_gain = recall_improvement * total_predictions * 2000
        business_impact_estimate = fp_cost_savings + tp_revenue_gain
        
        return BacktestResult(
            stressor_name=new_stressor_column,
            baseline_accuracy=avg_baseline_accuracy,
            enhanced_accuracy=avg_enhanced_accuracy,
            accuracy_improvement=accuracy_improvement,
            baseline_precision=avg_baseline_precision,
            enhanced_precision=avg_enhanced_precision,
            precision_improvement=precision_improvement,
            baseline_recall=avg_baseline_recall,
            enhanced_recall=avg_enhanced_recall,
            recall_improvement=recall_improvement,
            roc_auc_improvement=roc_auc_improvement,
            false_positive_reduction=avg_fp_reduction,
            business_impact_estimate=business_impact_estimate,
            statistical_significance=accuracy_improvement_significance
        )
    
    def _calculate_correlation_ci(self, 
                                 correlation: float, 
                                 sample_size: int, 
                                 confidence_level: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for correlation coefficient"""
        # Fisher's Z transformation
        z = np.arctanh(correlation)
        z_se = 1 / np.sqrt(sample_size - 3)
        
        # Z critical value
        alpha = 1 - confidence_level
        z_critical = stats.norm.ppf(1 - alpha/2)
        
        # Confidence interval in Z space
        z_lower = z - z_critical * z_se
        z_upper = z + z_critical * z_se
        
        # Transform back to correlation space
        r_lower = np.tanh(z_lower)
        r_upper = np.tanh(z_upper)
        
        return (r_lower, r_upper)
    
    def _calculate_statistical_power(self, 
                                   effect_size: float, 
                                   sample_size: int, 
                                   alpha: float) -> Dict:
        """Calculate statistical power for the test"""
        from scipy.stats import norm
        
        # Simplified power calculation for correlation
        if effect_size == 0:
            power = alpha  # Type I error rate when null is true
        else:
            # Calculate non-centrality parameter
            z_alpha = norm.ppf(1 - alpha/2)
            z_beta = (np.sqrt(sample_size - 3) * np.arctanh(effect_size)) - z_alpha
            power = 1 - norm.cdf(z_beta)
        
        return {
            "power": power,
            "effect_size": effect_size,
            "sample_size": sample_size,
            "alpha": alpha,
            "adequate_power": power >= 0.8
        }
    
    def multiple_testing_correction(self, 
                                  validation_results: List[ValidationResult],
                                  method: str = "bonferroni") -> List[ValidationResult]:
        """Apply multiple testing correction to validation results"""
        p_values = [result.p_value for result in validation_results]
        
        if method == "bonferroni":
            adjusted_alpha = self.significance_level / len(p_values)
            corrected_results = []
            
            for result in validation_results:
                # Update significance based on corrected alpha
                result.statistical_significance = result.p_value < adjusted_alpha
                
                # Update recommendation
                if result.statistical_significance and result.practical_significance:
                    result.recommendation = "ACCEPT: Significant after multiple testing correction"
                elif result.p_value < self.significance_level:  # Significant before correction
                    result.recommendation = "CONDITIONAL: Significant before but not after correction"
                else:
                    result.recommendation = "REJECT: Not significant"
                
                corrected_results.append(result)
            
            return corrected_results
        
        else:
            raise ValueError(f"Correction method {method} not implemented")
    
    def generate_validation_report(self, 
                                 validation_results: List[ValidationResult],
                                 backtest_results: List[BacktestResult]) -> Dict:
        """Generate comprehensive validation report"""
        
        # Summary statistics
        total_stressors_tested = len(validation_results)
        statistically_significant = sum(1 for r in validation_results if r.statistical_significance)
        practically_significant = sum(1 for r in validation_results if r.practical_significance)
        recommended_for_adoption = sum(1 for r in validation_results if "ACCEPT" in r.recommendation)
        
        # Best performing stressors
        best_correlation = max(validation_results, key=lambda x: abs(x.correlation_coefficient))
        best_backtest = max(backtest_results, key=lambda x: x.accuracy_improvement) if backtest_results else None
        
        # Business impact
        total_business_impact = sum(r.business_impact_estimate for r in backtest_results)
        
        report = {
            "validation_summary": {
                "total_stressors_tested": total_stressors_tested,
                "statistically_significant": statistically_significant,
                "practically_significant": practically_significant,
                "recommended_for_adoption": recommended_for_adoption,
                "significance_rate": statistically_significant / total_stressors_tested if total_stressors_tested > 0 else 0
            },
            "best_performers": {
                "highest_correlation": {
                    "stressor": best_correlation.stressor_name,
                    "correlation": best_correlation.correlation_coefficient,
                    "p_value": best_correlation.p_value
                },
                "best_backtest": {
                    "stressor": best_backtest.stressor_name if best_backtest else None,
                    "accuracy_improvement": best_backtest.accuracy_improvement if best_backtest else None,
                    "business_impact": best_backtest.business_impact_estimate if best_backtest else None
                } if best_backtest else None
            },
            "business_impact": {
                "total_estimated_value": total_business_impact,
                "average_accuracy_improvement": np.mean([r.accuracy_improvement for r in backtest_results]) if backtest_results else 0,
                "average_fp_reduction": np.mean([r.false_positive_reduction for r in backtest_results]) if backtest_results else 0
            },
            "recommendations": [
                {
                    "stressor": result.stressor_name,
                    "recommendation": result.recommendation,
                    "correlation": result.correlation_coefficient,
                    "p_value": result.p_value,
                    "effect_size": result.effect_size
                }
                for result in validation_results
            ],
            "methodology": {
                "significance_level": self.significance_level,
                "minimum_effect_size": self.min_effect_size,
                "multiple_testing_correction": "bonferroni",
                "validation_timestamp": datetime.utcnow().isoformat()
            }
        }
        
        return report


# Example usage and testing
def example_validation():
    """Example of how to use the validation framework"""
    
    # Generate sample data
    np.random.seed(42)
    n_samples = 1000
    
    # Simulate stressor data
    traffic_density = np.random.gamma(2, 2, n_samples)  # Traffic density
    road_quality = np.random.normal(50, 15, n_samples)  # Road quality score
    economic_stress = np.random.beta(2, 5, n_samples)   # Economic stress index
    
    # Simulate battery failure with realistic correlations
    failure_prob = (
        0.1 +  # Base failure rate
        0.05 * (traffic_density - traffic_density.mean()) / traffic_density.std() +  # Traffic effect
        0.03 * (road_quality.mean() - road_quality) / road_quality.std() +  # Road quality effect
        0.02 * (economic_stress - economic_stress.mean()) / economic_stress.std()  # Economic effect
    )
    
    failure_prob = np.clip(failure_prob, 0, 1)
    battery_failure = np.random.binomial(1, failure_prob, n_samples)
    
    # Create validation framework
    validator = StatisticalValidationFramework(significance_level=0.01, min_effect_size=0.1)
    
    # Validate each stressor
    traffic_result = validator.validate_correlation(
        traffic_density, battery_failure, "traffic_density", "continuous"
    )
    
    road_result = validator.validate_correlation(
        road_quality, battery_failure, "road_quality", "continuous"
    )
    
    economic_result = validator.validate_correlation(
        economic_stress, battery_failure, "economic_stress", "continuous"
    )
    
    # Apply multiple testing correction
    all_results = [traffic_result, road_result, economic_result]
    corrected_results = validator.multiple_testing_correction(all_results)
    
    # Generate report
    report = validator.generate_validation_report(corrected_results, [])
    
    return report


if __name__ == "__main__":
    report = example_validation()
    print(json.dumps(report, indent=2))