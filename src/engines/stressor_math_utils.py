"""
Stressor Mathematics Utilities
Implements the correct interpolated likelihood ratio formula for risk calculations
"""

from typing import Dict, List, Tuple
import numpy as np


def calculate_interpolated_likelihood_ratio(stressor_impacts: Dict[str, Tuple[float, float]]) -> float:
    """
    Calculate combined likelihood ratio using interpolated formula
    
    Formula: ∏(1 + (likelihood_ratio_i - 1) × stressor_intensity_i)
    
    Why not naive LR × intensity?
    This interpolated approach is superior for real-world scaling because:
    - It avoids overinflating failure rates at high LR and intensity
      (e.g., LR=10x at 90% would give 900% failure rate with naive approach!)
    - It respects that intensity = 0 should yield no risk impact (multiplier = 1)
      (naive approach would give 0x multiplier, incorrectly eliminating base risk)
    - It keeps outputs interpretable and bounded vs exponential explosion
    - Example: LR=10x at 90% intensity → 9.1x (not 9.0x), preserving baseline
    
    Mathematical properties:
    - When intensity = 0: multiplier = 1 (no effect)
    - When intensity = 1: multiplier = LR (full effect)
    - When 0 < intensity < 1: smooth interpolation between the two
    
    Args:
        stressor_impacts: Dict mapping stressor_name to (likelihood_ratio, intensity)
                         where likelihood_ratio is the multiplier at full intensity
                         and intensity is 0.0-1.0
    
    Returns:
        Combined likelihood ratio
    
    Example:
        stressor_impacts = {
            "cold_weather": (6.50, 0.87),  # 6.5x multiplier at 87% intensity
            "short_trips": (2.83, 0.76)    # 2.83x multiplier at 76% intensity
        }
        result = calculate_interpolated_likelihood_ratio(stressor_impacts)
        # Returns: 5.785 × 2.3908 = 13.83
    """
    combined_lr = 1.0
    
    for stressor_name, (likelihood_ratio, intensity) in stressor_impacts.items():
        # Validate inputs
        if likelihood_ratio < 0:
            raise ValueError(f"Likelihood ratio for {stressor_name} must be positive")
        if not 0 <= intensity <= 1:
            raise ValueError(f"Intensity for {stressor_name} must be between 0 and 1")
        
        # Apply interpolated formula: 1 + (LR - 1) × intensity
        effective_multiplier = 1 + (likelihood_ratio - 1) * intensity
        combined_lr *= effective_multiplier
    
    return combined_lr


def calculate_risk_probability(base_rate: float, 
                             stressor_impacts: Dict[str, Tuple[float, float]]) -> float:
    """
    Calculate final risk probability using interpolated likelihood ratios
    
    Formula: P(failure|stressors) = P(failure) × ∏(1 + (LR_i - 1) × intensity_i)
    
    Args:
        base_rate: Base failure probability (0-1)
        stressor_impacts: Dict mapping stressor to (likelihood_ratio, intensity)
    
    Returns:
        Final risk probability (bounded 0-1)
        
    Example:
        base_rate = 0.023  # 2.3% industry failure rate
        stressor_impacts = {
            "cold_weather": (6.50, 0.87),
            "short_trips": (2.83, 0.76)
        }
        risk = calculate_risk_probability(base_rate, stressor_impacts)
        # Returns: 0.318 (31.8%)
    """
    combined_lr = calculate_interpolated_likelihood_ratio(stressor_impacts)
    risk = base_rate * combined_lr
    
    # Ensure bounded between 0 and 1
    return max(0.0, min(1.0, risk))


def decompose_risk_calculation(base_rate: float,
                              stressor_impacts: Dict[str, Tuple[float, float]]) -> Dict:
    """
    Provide detailed breakdown of risk calculation for transparency
    
    Returns dict with intermediate calculations for debugging/explanation
    """
    breakdown = {
        "base_rate": base_rate,
        "stressor_contributions": {},
        "combined_likelihood_ratio": 1.0,
        "final_risk": 0.0,
        "calculation_steps": []
    }
    
    # Step 1: Base rate
    breakdown["calculation_steps"].append(f"Starting with base rate: {base_rate:.3f} ({base_rate*100:.1f}%)")
    
    # Step 2: Calculate each stressor contribution
    cumulative_lr = 1.0
    for stressor_name, (lr, intensity) in stressor_impacts.items():
        effective_multiplier = 1 + (lr - 1) * intensity
        breakdown["stressor_contributions"][stressor_name] = {
            "likelihood_ratio": lr,
            "intensity": intensity,
            "effective_multiplier": effective_multiplier,
            "formula": f"1 + ({lr} - 1) × {intensity} = {effective_multiplier:.3f}"
        }
        cumulative_lr *= effective_multiplier
        breakdown["calculation_steps"].append(
            f"{stressor_name}: {lr}x at {intensity*100:.0f}% intensity → {effective_multiplier:.3f}x multiplier"
        )
    
    breakdown["combined_likelihood_ratio"] = cumulative_lr
    breakdown["calculation_steps"].append(f"Combined likelihood ratio: {cumulative_lr:.3f}")
    
    # Step 3: Final risk
    final_risk = base_rate * cumulative_lr
    final_risk_bounded = max(0.0, min(1.0, final_risk))
    breakdown["final_risk"] = final_risk_bounded
    breakdown["calculation_steps"].append(
        f"Final risk: {base_rate:.3f} × {cumulative_lr:.3f} = {final_risk:.3f} ({final_risk_bounded*100:.1f}%)"
    )
    
    return breakdown


# Example usage and validation
if __name__ == "__main__":
    # Recreate the example from the documentation
    base_rate = 0.023  # 2.3% industry failure rate
    
    stressor_impacts = {
        "soc_decline": (6.50, 0.87),  # Cold weather impact
        "trip_cycling": (2.83, 0.76)  # Short trip stress
    }
    
    # Calculate risk
    risk = calculate_risk_probability(base_rate, stressor_impacts)
    print(f"Calculated risk: {risk:.3f} ({risk*100:.1f}%)")
    
    # Show breakdown
    breakdown = decompose_risk_calculation(base_rate, stressor_impacts)
    print("\nDetailed breakdown:")
    for step in breakdown["calculation_steps"]:
        print(f"  {step}")
    
    # Validate against expected result
    expected = 0.318
    assert abs(risk - expected) < 0.001, f"Expected {expected}, got {risk}"
    print(f"\n✅ Validation passed! Risk calculation matches documented example.")